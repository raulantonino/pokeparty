from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from roster.models import RosterEntry
from roster.services.roster import capture_pokemon

from .helpers import build_uniform_pokemon_data


class RosterViewTests(TestCase):
    def test_dashboard_returns_200(self):
        response = self.client.get(reverse("roster:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pokeparty")

    @patch("roster.views.get_random_pokemon_by_type")
    def test_capture_view_creates_entry_and_redirects_to_party_anchor(self, mocked_get_random):
        mocked_get_random.return_value = build_uniform_pokemon_data(25, 55, primary_type="electric")

        response = self.client.post(
            reverse("roster:capture"),
            {
                "pokemon_type": "electric",
                "sort_party": "position",
                "sort_box": "position",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(RosterEntry.objects.count(), 1)
        self.assertIn("#party-section", response["Location"])

    @patch("roster.views.get_random_pokemon_by_type")
    def test_capture_view_duplicate_redirects_to_capture_anchor(self, mocked_get_random):
        mocked_get_random.return_value = build_uniform_pokemon_data(4, 45, primary_type="fire")

        self.client.post(
            reverse("roster:capture"),
            {
                "pokemon_type": "fire",
                "sort_party": "position",
                "sort_box": "position",
            },
        )

        response = self.client.post(
            reverse("roster:capture"),
            {
                "pokemon_type": "fire",
                "sort_party": "position",
                "sort_box": "position",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(RosterEntry.objects.count(), 1)
        self.assertIn("#capture-section", response["Location"])

    def test_optimize_view_redirects_to_party_anchor(self):
        for external_id in range(1, 8):
            capture_pokemon(build_uniform_pokemon_data(external_id, 20 + external_id))

        response = self.client.post(
            reverse("roster:optimize"),
            {
                "sort_party": "position",
                "sort_box": "position",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("#party-section", response["Location"])

    def test_release_view_from_box_redirects_to_box_anchor(self):
        for external_id in range(1, 8):
            capture_pokemon(build_uniform_pokemon_data(external_id, 20 + external_id))

        box_entry = RosterEntry.objects.in_box().first()

        response = self.client.post(
            reverse("roster:release", args=[box_entry.id]),
            {
                "sort_party": "position",
                "sort_box": "position",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("#box-section", response["Location"])

    def test_release_view_from_party_redirects_to_party_anchor(self):
        for external_id in range(1, 9):
            capture_pokemon(build_uniform_pokemon_data(external_id, 20 + external_id))

        party_entry = RosterEntry.objects.in_party().get(position=1)

        response = self.client.post(
            reverse("roster:release", args=[party_entry.id]),
            {
                "sort_party": "position",
                "sort_box": "position",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("#party-section", response["Location"])