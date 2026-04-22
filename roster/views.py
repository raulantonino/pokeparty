from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import PokemonTypeSelectionForm
from .models import PokemonType, RosterEntry
from .services.pokeapi import PokeAPIError, get_random_pokemon_by_type
from .services.roster import (
    RosterError,
    capture_pokemon,
    get_captured_external_ids,
    get_sorted_entries,
    normalize_sort_key,
    optimize_best_team,
    release_box_pokemon,
)

SORT_OPTIONS = [
    ("position", "Posición"),
    ("hp", "HP"),
    ("attack", "ATK"),
    ("defense", "DEF"),
    ("speed", "SPE"),
    ("total_power", "Total"),
]


def build_dashboard_url(sort_party: str, sort_box: str) -> str:
    params = urlencode(
        {
            "sort_party": normalize_sort_key(sort_party),
            "sort_box": normalize_sort_key(sort_box),
        }
    )
    return f"{reverse('roster:dashboard')}?{params}"


@require_GET
def dashboard_view(request):
    sort_party = normalize_sort_key(request.GET.get("sort_party", "position"))
    sort_box = normalize_sort_key(request.GET.get("sort_box", "position"))

    party_entries = get_sorted_entries(RosterEntry.Location.PARTY, sort_party)
    box_entries = get_sorted_entries(RosterEntry.Location.BOX, sort_box)

    context = {
        "page_title": "Pokeparty",
        "pokemon_types": PokemonType.choices,
        "party_entries": party_entries,
        "box_entries": box_entries,
        "sort_party": sort_party,
        "sort_box": sort_box,
        "sort_options": SORT_OPTIONS,
    }
    return render(request, "roster/dashboard.html", context)


@require_POST
def capture_pokemon_view(request):
    sort_party = request.POST.get("sort_party", "position")
    sort_box = request.POST.get("sort_box", "position")
    form = PokemonTypeSelectionForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Debes seleccionar un tipo válido.")
        return redirect(build_dashboard_url(sort_party, sort_box))

    pokemon_type = form.cleaned_data["pokemon_type"]

    try:
        normalized_pokemon = get_random_pokemon_by_type(
            pokemon_type,
            excluded_external_ids=get_captured_external_ids(),
        )
        roster_entry, sent_to_party = capture_pokemon(normalized_pokemon)
    except PokeAPIError as exc:
        messages.error(request, str(exc))
        return redirect(build_dashboard_url(sort_party, sort_box))
    except RosterError as exc:
        messages.warning(request, str(exc))
        return redirect(build_dashboard_url(sort_party, sort_box))

    destination = "Party" if sent_to_party else "PC Box"
    messages.success(
        request,
        f"{roster_entry.pokemon.display_name} fue capturado y enviado a {destination}.",
    )
    return redirect(build_dashboard_url(sort_party, sort_box))


@require_POST
def optimize_best_team_view(request):
    sort_party = request.POST.get("sort_party", "position")
    sort_box = request.POST.get("sort_box", "position")

    try:
        party_count, box_count = optimize_best_team()
    except RosterError as exc:
        messages.warning(request, str(exc))
        return redirect(build_dashboard_url(sort_party, sort_box))

    messages.success(
        request,
        f"Equipo optimizado: {party_count} Pokémon quedaron en la Party y {box_count} en la PC Box.",
    )
    return redirect(build_dashboard_url(sort_party, sort_box))


@require_POST
def release_pokemon_view(request, entry_id: int):
    sort_party = request.POST.get("sort_party", "position")
    sort_box = request.POST.get("sort_box", "position")

    roster_entry = get_object_or_404(
        RosterEntry.objects.with_pokemon(),
        pk=entry_id,
    )

    try:
        pokemon_name = roster_entry.pokemon.display_name
        release_box_pokemon(roster_entry)
    except RosterError as exc:
        messages.error(request, str(exc))
        return redirect(build_dashboard_url(sort_party, sort_box))

    messages.success(request, f"{pokemon_name} fue liberado de la PC Box.")
    return redirect(build_dashboard_url(sort_party, sort_box))