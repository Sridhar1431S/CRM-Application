from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.leads.serializers import LeadAssignSerializer, LeadSerializer
from tests.factories import create_admin, create_sales_rep


def valid_payload(**overrides):
    payload = {
        "company_name": "  Prospect Inc  ",
        "contact_name": "  Ravi Kumar  ",
        "email": "ravi@prospect.test",
        "phone_number": "+91 9111111111",
        "source": "Referral",
        "priority": "high",
        "status": "new",
    }
    payload.update(overrides)
    return payload


class LeadSerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()

    def test_trims_company_and_contact_name(self):
        serializer = LeadSerializer(data=valid_payload())

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["company_name"], "Prospect Inc")
        self.assertEqual(serializer.validated_data["contact_name"], "Ravi Kumar")

    def test_blank_company_and_contact_name_are_rejected(self):
        serializer = LeadSerializer(data=valid_payload(company_name=" ", contact_name=" "))

        self.assertFalse(serializer.is_valid())
        self.assertIn("company_name", serializer.errors)
        self.assertIn("contact_name", serializer.errors)

    def test_field_validators_reject_whitespace_only_values(self):
        serializer = LeadSerializer()

        with self.assertRaises(ValidationError):
            serializer.validate_company_name("   ")
        with self.assertRaises(ValidationError):
            serializer.validate_contact_name("   ")

    def test_assigned_rep_validator_rejects_a_non_rep_user(self):
        serializer = LeadSerializer()

        with self.assertRaises(ValidationError):
            serializer.validate_assigned_rep(self.admin)
        self.assertEqual(serializer.validate_assigned_rep(self.rep), self.rep)
        self.assertIsNone(serializer.validate_assigned_rep(None))

    def test_invalid_phone_number_is_rejected(self):
        serializer = LeadSerializer(data=valid_payload(phone_number="abc"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_lead_can_be_assigned_to_a_sales_rep(self):
        serializer = LeadSerializer(data=valid_payload(assigned_rep=str(self.rep.id)))

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["assigned_rep"], self.rep)

    def test_lead_cannot_be_assigned_to_an_administrator(self):
        serializer = LeadSerializer(data=valid_payload(assigned_rep=str(self.admin.id)))

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_rep", serializer.errors)

    def test_converted_flag_is_read_only(self):
        serializer = LeadSerializer(data=valid_payload(converted_to_opportunity=True))

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("converted_to_opportunity", serializer.validated_data)


class LeadAssignSerializerTests(TestCase):
    def test_accepts_an_active_sales_rep(self):
        rep = create_sales_rep()

        serializer = LeadAssignSerializer(data={"assigned_rep": str(rep.id)})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["assigned_rep"], rep)

    def test_rejects_a_disabled_sales_rep(self):
        rep = create_sales_rep(is_active=False)

        serializer = LeadAssignSerializer(data={"assigned_rep": str(rep.id)})

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_rep", serializer.errors)

    def test_rejects_an_administrator(self):
        admin = create_admin()

        serializer = LeadAssignSerializer(data={"assigned_rep": str(admin.id)})

        self.assertFalse(serializer.is_valid())
        self.assertIn("assigned_rep", serializer.errors)
