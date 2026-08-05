from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import create_admin, create_sales_rep


class SalesRepViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()

    def test_list_contains_only_sales_reps(self):
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("sales_reps:sales-rep-list"))

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.rep.id))

    def test_admin_can_create_a_rep(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse("sales_reps:sales-rep-list"),
            {"name": "New Rep", "email": "new@crmlite.test", "password": "Str0ng!Passw0rd"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)

    def test_sales_rep_cannot_create_a_rep(self):
        self.client.force_authenticate(self.rep)

        response = self.client.post(reverse("sales_reps:sales-rep-list"), {}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_disable_and_enable_actions_toggle_status(self):
        self.client.force_authenticate(self.admin)

        disabled = self.client.patch(reverse("sales_reps:sales-rep-disable", args=[self.rep.id]))
        self.assertEqual(disabled.status_code, 200)
        self.assertFalse(disabled.data["is_active"])
        self.rep.refresh_from_db()
        self.assertFalse(self.rep.is_active)

        enabled = self.client.patch(reverse("sales_reps:sales-rep-enable", args=[self.rep.id]))
        self.assertEqual(enabled.status_code, 200)
        self.assertTrue(enabled.data["is_active"])

    def test_reps_cannot_be_hard_deleted(self):
        self.client.force_authenticate(self.admin)

        response = self.client.delete(reverse("sales_reps:sales-rep-detail", args=[self.rep.id]))

        self.assertEqual(response.status_code, 405)
