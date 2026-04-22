from django import forms

from .models import PokemonType


class PokemonTypeSelectionForm(forms.Form):
    pokemon_type = forms.ChoiceField(
        choices=PokemonType.choices,
        widget=forms.RadioSelect,
        label="Tipo de Pokémon",
    )