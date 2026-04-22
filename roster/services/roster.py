from django.db import transaction

from roster.models import Pokemon, RosterEntry


class RosterError(Exception):
    pass


def get_next_position(location: str) -> int:
    last_entry = (
        RosterEntry.objects.filter(location=location)
        .order_by("-position")
        .first()
    )
    return 1 if last_entry is None else last_entry.position + 1


@transaction.atomic
def capture_pokemon(normalized_pokemon_data: dict) -> tuple[RosterEntry, bool]:
    external_id = normalized_pokemon_data["external_id"]

    if RosterEntry.objects.filter(pokemon__external_id=external_id).exists():
        raise RosterError("Ese Pokémon ya fue capturado y no se permiten duplicados.")

    pokemon, _ = Pokemon.objects.get_or_create(
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


def release_box_pokemon(roster_entry: RosterEntry) -> None:
    if roster_entry.location != RosterEntry.Location.BOX:
        raise RosterError("Solo puedes liberar Pokémon desde la PC Box.")

    roster_entry.delete()