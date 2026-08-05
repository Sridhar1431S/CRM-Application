from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.followups.serializers import FollowUpSerializer
from tests.factories import create_followup, create_opportunity, create_sales_rep


class FollowUpSerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rep = create_sales_rep()
        cls.opportunity = create_opportunity(assigned_rep=cls.rep)

    def test_note_is_trimmed(self):
        serializer = FollowUpSerializer(
            data={"opportunity": str(self.opportunity.id), "note": "  Sent the proposal.  "}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["note"], "Sent the proposal.")

    def test_whitespace_only_note_is_rejected(self):
        serializer = FollowUpSerializer(data={"opportunity": str(self.opportunity.id), "note": "   "})

        self.assertFalse(serializer.is_valid())
        self.assertIn("note", serializer.errors)

    def test_note_validator_rejects_whitespace_only_values(self):
        with self.assertRaises(ValidationError):
            FollowUpSerializer().validate_note("   ")

    def test_next_followup_date_is_optional(self):
        serializer = FollowUpSerializer(
            data={
                "opportunity": str(self.opportunity.id),
                "note": "No follow-up needed yet.",
                "next_followup_date": None,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_created_by_is_read_only_and_exposed_as_nested_detail(self):
        followup = create_followup(
            opportunity=self.opportunity,
            created_by=self.rep,
            next_followup_date=timezone.localdate() + timedelta(days=1),
        )

        data = FollowUpSerializer(followup).data

        self.assertEqual(data["created_by_detail"]["email"], self.rep.email)
        self.assertEqual(data["created_by"], self.rep.id)
