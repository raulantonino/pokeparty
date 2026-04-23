from django.test import TestCase

from roster.models import RosterEntry
from roster.services.roster import (
    RosterError,
    capture_pokemon,
    get_sorted_entries,
    optimize_best_team,
    release_pokemon,
)

from .helpers import build_pokemon_data, build_uniform_pokemon_data


class RosterServiceTests(TestCase):
    def test_first_six_captures_go_to_party_and_seventh_goes_to_box(self):
        last_entry = None
        sent_to_party = None

        for external_id in range(1, 8):
            last_entry, sent_to_party = capture_pokemon(
                build_uniform_pokemon_data(external_id, 30 + external_id)
            )

        self.assertEqual(RosterEntry.objects.in_party().count(), 6)
        self.assertEqual(RosterEntry.objects.in_box().count(), 1)
        self.assertEqual(last_entry.location, RosterEntry.Location.BOX)
        self.assertFalse(sent_to_party)

    def test_capture_rejects_duplicates(self):
        capture_pokemon(build_uniform_pokemon_data(1, 40))

        with self.assertRaisesMessage(
            RosterError,
            "Ese Pokémon ya fue capturado y no se permiten duplicados.",
        ):
            capture_pokemon(build_uniform_pokemon_data(1, 40))

    def test_sort_by_total_power_returns_descending_order(self):
        capture_pokemon(build_uniform_pokemon_data(1, 20))
        capture_pokemon(build_uniform_pokemon_data(2, 50))
        capture_pokemon(build_uniform_pokemon_data(3, 35))

        entries = get_sorted_entries(RosterEntry.Location.PARTY, "total_power")
        ordered_ids = [entry.pokemon.external_id for entry in entries]

        self.assertEqual(ordered_ids, [2, 3, 1])

    def test_release_from_box_compacts_positions(self):
        for external_id in range(1, 9):
            capture_pokemon(build_uniform_pokemon_data(external_id, 20 + external_id))

        box_entries = list(RosterEntry.objects.in_box().order_by("position"))
        self.assertEqual(len(box_entries), 2)
        self.assertEqual(box_entries[0].position, 1)
        self.assertEqual(box_entries[1].position, 2)

        release_pokemon(box_entries[0])

        remaining_box = list(RosterEntry.objects.in_box().order_by("position"))
        self.assertEqual(len(remaining_box), 1)
        self.assertEqual(remaining_box[0].position, 1)

    def test_release_from_party_promotes_strongest_box_pokemon(self):
        for external_id in range(1, 7):
            capture_pokemon(build_uniform_pokemon_data(external_id, 20 + external_id))

        capture_pokemon(build_uniform_pokemon_data(7, 90, primary_type="dragon"))
        capture_pokemon(build_uniform_pokemon_data(8, 70, primary_type="grass"))

        party_entry = RosterEntry.objects.in_party().get(position=2)
        promoted_name = release_pokemon(party_entry)

        promoted_entry = RosterEntry.objects.get(pokemon__external_id=7)

        self.assertEqual(promoted_name, promoted_entry.pokemon.display_name)
        self.assertEqual(promoted_entry.location, RosterEntry.Location.PARTY)
        self.assertEqual(promoted_entry.position, 2)
        self.assertEqual(RosterEntry.objects.in_party().count(), 6)
        self.assertEqual(RosterEntry.objects.in_box().count(), 1)

    def test_optimize_best_team_keeps_strongest_six(self):
        stat_values = {
            1: 10,
            2: 20,
            3: 30,
            4: 40,
            5: 50,
            6: 60,
            7: 70,
            8: 80,
            9: 90,
        }

        for external_id, stat_value in stat_values.items():
            capture_pokemon(build_uniform_pokemon_data(external_id, stat_value))

        party_count, box_count = optimize_best_team()

        party_ids = set(
            RosterEntry.objects.in_party().values_list("pokemon__external_id", flat=True)
        )

        self.assertEqual(party_count, 6)
        self.assertEqual(box_count, 3)
        self.assertEqual(party_ids, {4, 5, 6, 7, 8, 9})

    def test_optimize_best_team_uses_diversity_on_ties(self):
        tied_payloads = [
            build_pokemon_data(
                1,
                primary_type="fire",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
            build_pokemon_data(
                2,
                primary_type="fire",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
            build_pokemon_data(
                3,
                primary_type="water",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
            build_pokemon_data(
                4,
                primary_type="grass",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
            build_pokemon_data(
                5,
                primary_type="electric",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
            build_pokemon_data(
                6,
                primary_type="psychic",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
            build_pokemon_data(
                7,
                primary_type="dragon",
                hp=50, attack=50, defense=50, special_attack=50, special_defense=50, speed=50,
            ),
        ]

        for payload in tied_payloads:
            capture_pokemon(payload)

        optimize_best_team()

        party_types = list(
            RosterEntry.objects.in_party()
            .select_related("pokemon")
            .values_list("pokemon__primary_type", flat=True)
        )

        self.assertEqual(len(party_types), 6)
        self.assertGreaterEqual(len(set(party_types)), 6)