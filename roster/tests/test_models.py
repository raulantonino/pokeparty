from django.test import TestCase

from roster.models import Pokemon, RosterEntry

from .helpers import build_pokemon_data


class PokemonModelTests(TestCase):
    def test_pokemon_computed_properties(self):
        pokemon = Pokemon.objects.create(
            **build_pokemon_data(
                6,
                name="charizard",
                primary_type="fire",
                secondary_type="flying",
                hp=78,
                attack=84,
                defense=78,
                special_attack=109,
                special_defense=85,
                speed=100,
            )
        )

        self.assertEqual(pokemon.display_name, "Charizard")
        self.assertEqual(pokemon.total_power, 534)
        self.assertEqual(pokemon.dominant_stat_name, "special_attack")
        self.assertEqual(pokemon.dominant_stat_value, 109)
        self.assertEqual(str(pokemon), "#6 Charizard")

    def test_roster_entry_total_power_comes_from_pokemon(self):
        pokemon = Pokemon.objects.create(
            **build_pokemon_data(
                25,
                name="pikachu",
                primary_type="electric",
                hp=35,
                attack=55,
                defense=40,
                special_attack=50,
                special_defense=50,
                speed=90,
            )
        )

        entry = RosterEntry.objects.create(
            pokemon=pokemon,
            location=RosterEntry.Location.PARTY,
            position=1,
        )

        self.assertEqual(entry.total_power, 320)
        self.assertEqual(str(entry), "Pikachu - Party #1")