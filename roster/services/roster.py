from django.db import transaction

from roster.models import Pokemon, RosterEntry


class RosterError(Exception):
    pass


SORT_FIELD_MAP = {
    "position": "position",
    "hp": "pokemon__hp",
    "attack": "pokemon__attack",
    "defense": "pokemon__defense",
    "speed": "pokemon__speed",
}
ALLOWED_SORT_KEYS = set(SORT_FIELD_MAP.keys()) | {"total_power"}


def normalize_sort_key(sort_key: str | None) -> str:
    if sort_key in ALLOWED_SORT_KEYS:
        return sort_key
    return "position"


def get_captured_external_ids() -> set[int]:
    return set(
        RosterEntry.objects.values_list("pokemon__external_id", flat=True)
    )


def get_next_position(location: str) -> int:
    last_entry = (
        RosterEntry.objects.filter(location=location)
        .order_by("-position")
        .first()
    )
    return 1 if last_entry is None else last_entry.position + 1


def compact_positions(location: str) -> None:
    entries = list(
        RosterEntry.objects.filter(location=location)
        .with_pokemon()
        .order_by("position", "pokemon__external_id")
    )

    for index, entry in enumerate(entries, start=1):
        if entry.position != index:
            entry.position = index
            entry.save(update_fields=["position", "updated_at"])


def get_sorted_entries(location: str, sort_key: str):
    sort_key = normalize_sort_key(sort_key)

    queryset = (
        RosterEntry.objects.filter(location=location)
        .with_pokemon()
    )

    if sort_key == "position":
        return queryset.order_by("position", "pokemon__external_id")

    if sort_key == "hp":
        return queryset.order_by("-pokemon__hp", "-pokemon__speed", "pokemon__external_id")

    if sort_key == "attack":
        return queryset.order_by("-pokemon__attack", "-pokemon__speed", "pokemon__external_id")

    if sort_key == "defense":
        return queryset.order_by("-pokemon__defense", "-pokemon__speed", "pokemon__external_id")

    if sort_key == "speed":
        return queryset.order_by("-pokemon__speed", "pokemon__external_id")

    if sort_key == "total_power":
        entries = list(queryset)
        return sorted(
            entries,
            key=lambda entry: (
                -entry.pokemon.total_power,
                -entry.pokemon.speed,
                entry.pokemon.external_id,
            ),
        )

    return queryset.order_by("position", "pokemon__external_id")


@transaction.atomic
def capture_pokemon(normalized_pokemon_data: dict) -> tuple[RosterEntry, bool]:
    external_id = normalized_pokemon_data["external_id"]

    if RosterEntry.objects.filter(pokemon__external_id=external_id).exists():
        raise RosterError("Ese Pokémon ya fue capturado y no se permiten duplicados.")

    pokemon, _ = Pokemon.objects.update_or_create(
        external_id=external_id,
        defaults=normalized_pokemon_data,
    )

    party_count = RosterEntry.objects.in_party().count()
    location = (
        RosterEntry.Location.PARTY
        if party_count < 6
        else RosterEntry.Location.BOX
    )
    position = get_next_position(location)

    roster_entry = RosterEntry.objects.create(
        pokemon=pokemon,
        location=location,
        position=position,
    )
    return roster_entry, location == RosterEntry.Location.PARTY


@transaction.atomic
def release_box_pokemon(roster_entry: RosterEntry) -> None:
    if roster_entry.location != RosterEntry.Location.BOX:
        raise RosterError("Solo puedes liberar Pokémon desde la PC Box.")

    roster_entry.delete()
    compact_positions(RosterEntry.Location.BOX)


def _entry_types(entry: RosterEntry) -> set[str]:
    types = {entry.pokemon.primary_type}
    if entry.pokemon.secondary_type:
        types.add(entry.pokemon.secondary_type)
    return types


def _adds_type_diversity(entry: RosterEntry, selected_types: set[str]) -> bool:
    return any(pokemon_type not in selected_types for pokemon_type in _entry_types(entry))


def _base_ranking(entry: RosterEntry) -> tuple[int, int, int, int]:
    return (
        -entry.pokemon.total_power,
        -entry.pokemon.dominant_stat_value,
        -entry.pokemon.speed,
        entry.pokemon.external_id,
    )


def _park_entries(entries: list[RosterEntry]) -> None:
    for index, entry in enumerate(entries, start=1000):
        entry.location = RosterEntry.Location.BOX
        entry.position = index
        entry.save(update_fields=["location", "position", "updated_at"])


def _apply_location_and_positions(entries: list[RosterEntry], location: str) -> None:
    for index, entry in enumerate(entries, start=1):
        entry.location = location
        entry.position = index
        entry.save(update_fields=["location", "position", "updated_at"])


@transaction.atomic
def optimize_best_team() -> tuple[int, int]:
    all_entries = list(
        RosterEntry.objects.with_pokemon().order_by(
            "location",
            "position",
            "pokemon__external_id",
        )
    )

    if not all_entries:
        raise RosterError("No hay Pokémon para optimizar todavía.")

    ranked_entries = sorted(all_entries, key=_base_ranking)

    selected_party: list[RosterEntry] = []
    selected_types: set[str] = set()
    remaining_entries = ranked_entries.copy()

    while remaining_entries and len(selected_party) < 6:
        current_best_power = remaining_entries[0].pokemon.total_power

        same_power_group = [
            entry
            for entry in remaining_entries
            if entry.pokemon.total_power == current_best_power
        ]
        remaining_entries = [
            entry
            for entry in remaining_entries
            if entry.pokemon.total_power != current_best_power
        ]

        while same_power_group and len(selected_party) < 6:
            same_power_group.sort(
                key=lambda entry: (
                    0 if _adds_type_diversity(entry, selected_types) else 1,
                    -entry.pokemon.dominant_stat_value,
                    -entry.pokemon.speed,
                    entry.pokemon.external_id,
                )
            )

            chosen_entry = same_power_group.pop(0)
            selected_party.append(chosen_entry)
            selected_types.update(_entry_types(chosen_entry))

    selected_ids = {entry.id for entry in selected_party}
    selected_box = [
        entry for entry in ranked_entries if entry.id not in selected_ids
    ]

    _park_entries(all_entries)
    _apply_location_and_positions(selected_party, RosterEntry.Location.PARTY)
    _apply_location_and_positions(selected_box, RosterEntry.Location.BOX)

    return len(selected_party), len(selected_box)