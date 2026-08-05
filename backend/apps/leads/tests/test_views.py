from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from tests.factories import create_admin, create_lead, create_sales_rep


class LeadViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.other_rep = create_sales_rep()

    def test_sales_rep_list_is_scoped_to_own_leads(self):
        own = create_lead(assigned_rep=self.rep)
        create_lead(assigned_rep=self.other_rep)
        create_lead()
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("leads:lead-list"))

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(own.id))

    def test_admin_list_shows_every_live_lead(self):
        create_lead(assigned_rep=self.rep)
        create_lead()
        create_lead(deleted_at=timezone.now())
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse("leads:lead-list"))

        self.assertEqual(response.data["count"], 2)

    def test_sales_rep_cannot_create_a_lead(self):
        self.client.force_authenticate(self.rep)

        response = self.client.post(reverse("leads:lead-list"), {}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_destroy_soft_deletes_the_lead(self):
        lead = create_lead()
        self.client.force_authenticate(self.admin)

        response = self.client.delete(reverse("leads:lead-detail", args=[lead.id]))

        self.assertEqual(response.status_code, 204)
        lead.refresh_from_db()
        self.assertIsNotNone(lead.deleted_at)

    def test_assign_action_sets_the_rep_and_advances_status(self):
        lead = create_lead()
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse("leads:lead-assign", args=[lead.id]),
            {"assigned_rep": str(self.rep.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["assigned_rep"], self.rep.id)
        lead.refresh_from_db()
        self.assertEqual(lead.status, Lead.Status.CONTACTED)

    def test_assign_action_is_forbidden_for_sales_reps(self):
        lead = create_lead(assigned_rep=self.rep)
        self.client.force_authenticate(self.rep)

        response = self.client.post(
            reverse("leads:lead-assign", args=[lead.id]),
            {"assigned_rep": str(self.rep.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_convert_action_creates_an_opportunity(self):
        lead = create_lead(assigned_rep=self.rep)
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse("leads:lead-convert", args=[lead.id]),
            {
                "estimated_value": "50000.00",
                "expected_closing_date": (timezone.localdate() + timedelta(days=10)).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["stage"], Opportunity.Stage.QUALIFICATION)
        lead.refresh_from_db()
        self.assertTrue(lead.converted_to_opportunity)

    def test_convert_action_requires_value_and_closing_date(self):
        lead = create_lead(assigned_rep=self.rep)
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse("leads:lead-convert", args=[lead.id]), {}, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Opportunity.objects.exists())

    def test_convert_action_surfaces_business_rule_violations_as_422(self):
        lead = create_lead()
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            reverse("leads:lead-convert", args=[lead.id]),
            {
                "estimated_value": "50000.00",
                "expected_closing_date": (timezone.localdate() + timedelta(days=10)).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "business_rule_violation")
