from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import PokemonTypeSelectionForm
from .models import RosterEntry
from .services.pokeapi import PokeAPIError, get_random_pokemon_by_type
from .services.roster import RosterError, capture_pokemon, release_box_pokemon


@require_GET
def dashboard_view(request):
    form = PokemonTypeSelectionForm()

    party_entries = (
        RosterEntry.objects.in_party()
        .with_pokemon()
        .order_by("position", "pokemon__external_id")
    )
    box_entries = (
        RosterEntry.objects.in_box()
        .with_pokemon()
        .order_by("position", "pokemon__external_id")
    )

    context = {
        "page_title": "Pokeparty",
        "form": form,
        "party_entries": party_entries,
        "box_entries": box_entries,
    }
    return render(request, "roster/dashboard.html", context)


@require_POST
def capture_pokemon_view(request):
    form = PokemonTypeSelectionForm(request.POST)

    if not form.is_valid():
        messages.error(request, "Debes seleccionar un tipo válido.")
        return redirect("roster:dashboard")

    pokemon_type = form.cleaned_data["pokemon_type"]

    try:
        normalized_pokemon = get_random_pokemon_by_type(pokemon_type)
        roster_entry, sent_to_party = capture_pokemon(normalized_pokemon)
    except PokeAPIError as exc:
        messages.error(request, str(exc))
        return redirect("roster:dashboard")
    except RosterError as exc:
        messages.warning(request, str(exc))
        return redirect("roster:dashboard")

    destination = "Party" if sent_to_party else "PC Box"
    messages.success(
        request,
        f"{roster_entry.pokemon.display_name} fue capturado y enviado a {destination}.",
    )
    return redirect("roster:dashboard")


@require_POST
def release_pokemon_view(request, entry_id: int):
    roster_entry = get_object_or_404(
        RosterEntry.objects.with_pokemon(),
        pk=entry_id,
    )

    try:
        pokemon_name = roster_entry.pokemon.display_name
        release_box_pokemon(roster_entry)
    except RosterError as exc:
        messages.error(request, str(exc))
        return redirect("roster:dashboard")

    messages.success(request, f"{pokemon_name} fue liberado de la PC Box.")
    return redirect("roster:dashboard")