from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.opportunities.models import Opportunity
from apps.opportunities.serializers import OpportunitySerializer, OpportunityStageUpdateSerializer
from tests.factories import create_admin, create_customer, create_opportunity, create_sales_rep


class OpportunitySerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()
        cls.customer = create_customer()

    def payload(self, **overrides):
        data = {
            "customer": str(self.customer.id),
            "assigned_rep": str(self.rep.id),
            "estimated_value": "50000.00",
            "expected_closing_date": (timezone.localdate() + timedelta(days=30)).isoformat(),
            "stage": Opportunity.Stage.QUALIFICATION,
        }
        data.update(overrides)
        return data

    def test_valid_payload(self):
        serializer = OpportunitySerializer(data=self.payload())

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_non_positive_value_is_rejected(self):
        for value in ["0", "-1.00"]:
            with self.subTest(value=value):
                serializer = OpportunitySerializer(data=self.payload(estimated_value=value))

                self.assertFalse(serializer.is_valid())
                self.assertIn("estimated_value", serializer.errors)

    def test_past_closing_date_is_rejected(self):
        past = (timezone.localdate() - timedelta(days=1)).isoformat()

        serializer = OpportunitySerializer(data=self.payload(expected_closing_date=past))

        self.assertFalse(serializer.is_valid())
        self.assertIn("expected_closing_date", serializer.errors)

    def test_todays_closing_date_is_accepted(self):
        today = timezone.localdate().isoformat()

        serializer = OpportunitySerializer(data=self.payload(expected_closing_date=today))

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_opportunity_cannot_be_assigned_to_an_administrator(self):
        serializer = OpportunitySerializer(data=self.payload(assigned_rep=str(self.admin.id)))

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_rep", serializer.errors)

    def test_assigned_rep_validator_rejects_a_non_rep_user(self):
        serializer = OpportunitySerializer()

        with self.assertRaises(ValidationError):
            serializer.validate_assigned_rep(self.admin)
        self.assertEqual(serializer.validate_assigned_rep(self.rep), self.rep)
        self.assertIsNone(serializer.validate_assigned_rep(None))

    def test_stage_change_on_closed_opportunity_is_rejected(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.WON)

        serializer = OpportunitySerializer(
            instance=opportunity, data={"stage": Opportunity.Stage.PROPOSAL}, partial=True
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("stage", serializer.errors)

    def test_stage_change_on_open_opportunity_is_allowed(self):
        opportunity = create_opportunity(assigned_rep=self.rep, stage=Opportunity.Stage.PROPOSAL)

        serializer = OpportunitySerializer(
            instance=opportunity, data={"stage": Opportunity.Stage.NEGOTIATION}, partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)


class OpportunityStageUpdateSerializerTests(TestCase):
    def test_accepts_known_stage(self):
        serializer = OpportunityStageUpdateSerializer(data={"stage": Opportunity.Stage.WON})

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_unknown_stage(self):
        serializer = OpportunityStageUpdateSerializer(data={"stage": "on-hold"})

        self.assertFalse(serializer.is_valid())
        self.assertIn("stage", serializer.errors)
