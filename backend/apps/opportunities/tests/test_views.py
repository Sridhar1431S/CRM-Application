from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.opportunities.models import Opportunity
from tests.factories import create_admin, create_opportunity, create_sales_rep


class OpportunityViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()
        self.other_rep = create_sales_rep()

    def test_sales_rep_list_is_scoped_to_own_opportunities(self):
        own = create_opportunity(assigned_rep=self.rep)
        create_opportunity(assigned_rep=self.other_rep)
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("opportunities:opportunity-list"))

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(own.id))

    def test_admin_list_shows_every_opportunity(self):
        create_opportunity(assigned_rep=self.rep)
        create_opportunity(assigned_rep=self.other_rep)
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse("opportunities:opportunity-list"))

        self.assertEqual(response.data["count"], 2)

    def test_sales_rep_cannot_create_or_delete(self):
        opportunity = create_opportunity(assigned_rep=self.rep)
        self.client.force_authenticate(self.rep)

        self.assertEqual(
            self.client.post(reverse("opportunities:opportunity-list"), {}, format="json").status_code, 403
        )
        self.assertEqual(
            self.client.delete(
                reverse("opportunities:opportunity-detail", args=[opportunity.id])
            ).status_code,
            403,
        )

    def test_assigned_rep_can_update_the_stage(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.PROPOSAL)
        self.client.force_authenticate(self.rep)

        response = self.client.patch(
            reverse("opportunities:opportunity-update-stage", args=[opportunity.id]),
            {"stage": Opportunity.Stage.NEGOTIATION},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["stage"], Opportunity.Stage.NEGOTIATION)

    def test_other_rep_cannot_see_or_update_the_opportunity(self):
        opportunity = create_opportunity(assigned_rep=self.other_rep)
        self.client.force_authenticate(self.rep)

        response = self.client.patch(
            reverse("opportunities:opportunity-update-stage", args=[opportunity.id]),
            {"stage": Opportunity.Stage.WON},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_closed_opportunity_stage_change_returns_422(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.WON)
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse("opportunities:opportunity-update-stage", args=[opportunity.id]),
            {"stage": Opportunity.Stage.PROPOSAL},
            format="json",
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "business_rule_violation")

    def test_unknown_stage_returns_400(self):
        opportunity = create_opportunity(assigned_rep=self.rep)
        self.client.force_authenticate(self.admin)

        response = self.client.patch(
            reverse("opportunities:opportunity-update-stage", args=[opportunity.id]),
            {"stage": "on-hold"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
