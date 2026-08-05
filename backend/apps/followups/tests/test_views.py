from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.followups.models import FollowUp
from tests.factories import create_admin, create_followup, create_opportunity, create_sales_rep


class OpportunityFollowUpViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.other_rep = create_sales_rep()
        self.opportunity = create_opportunity(assigned_rep=self.rep)
        self.url = reverse(
            "opportunity-followups:opportunity-followups", args=[self.opportunity.id]
        )

    def test_assigned_rep_can_list_the_history(self):
        create_followup(opportunity=self.opportunity, note="First call")
        self.client.force_authenticate(self.rep)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["note"], "First call")

    def test_assigned_rep_can_log_a_followup(self):
        self.client.force_authenticate(self.rep)

        response = self.client.post(
            self.url,
            {
                "opportunity": str(self.opportunity.id),
                "note": "Proposal sent.",
                "next_followup_date": (timezone.localdate() + timedelta(days=2)).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["created_by"], self.rep.id)
        self.assertEqual(FollowUp.objects.count(), 1)

    def test_admin_can_list_followups_on_any_opportunity(self):
        create_followup(opportunity=self.opportunity)
        self.client.force_authenticate(self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_body_must_repeat_the_opportunity_id_from_the_url(self):
        """The nested route ignores the body's `opportunity`, yet the serializer still requires it."""
        self.client.force_authenticate(self.rep)

        response = self.client.post(self.url, {"note": "Proposal sent."}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("opportunity", response.data["error"]["details"])

    def test_empty_note_is_rejected(self):
        self.client.force_authenticate(self.rep)

        response = self.client.post(
            self.url, {"opportunity": str(self.opportunity.id), "note": "   "}, format="json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(FollowUp.objects.exists())

    def test_other_rep_gets_404_for_a_foreign_opportunity(self):
        self.client.force_authenticate(self.other_rep)

        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(
            self.client.post(
                self.url, {"opportunity": str(self.opportunity.id), "note": "Hi"}, format="json"
            ).status_code,
            404,
        )


class UpcomingFollowUpsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.other_rep = create_sales_rep()

    def test_past_and_undated_followups_are_excluded(self):
        opportunity = create_opportunity(assigned_rep=self.rep)
        create_followup(opportunity=opportunity, next_followup_date=timezone.localdate())
        create_followup(
            opportunity=opportunity, next_followup_date=timezone.localdate() - timedelta(days=1)
        )
        create_followup(opportunity=opportunity, next_followup_date=None)
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse("followups:upcoming-followups"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_sales_rep_sees_only_own_upcoming_followups(self):
        create_followup(
            opportunity=create_opportunity(assigned_rep=self.rep),
            next_followup_date=timezone.localdate(),
        )
        create_followup(
            opportunity=create_opportunity(assigned_rep=self.other_rep),
            next_followup_date=timezone.localdate(),
        )
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("followups:upcoming-followups"))

        self.assertEqual(len(response.data), 1)

    def test_results_are_ordered_by_next_followup_date(self):
        opportunity = create_opportunity(assigned_rep=self.rep)
        later = create_followup(
            opportunity=opportunity, next_followup_date=timezone.localdate() + timedelta(days=5)
        )
        sooner = create_followup(
            opportunity=opportunity, next_followup_date=timezone.localdate() + timedelta(days=1)
        )
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("followups:upcoming-followups"))

        self.assertEqual([row["id"] for row in response.data], [str(sooner.id), str(later.id)])
