from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.customers.serializers import CustomerSerializer
from tests.factories import create_customer


def valid_payload(**overrides):
    payload = {
        "company_name": "  Acme Corp  ",
        "contact_person": "  Jane Doe  ",
        "email": "  Jane@Acme.TEST ",
        "phone_number": "+91 9000000001",
        "industry": "SaaS",
        "status": "prospect",
    }
    payload.update(overrides)
    return payload


class CustomerSerializerTests(TestCase):
    def test_trims_whitespace_and_normalizes_email_case(self):
        serializer = CustomerSerializer(data=valid_payload())

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["company_name"], "Acme Corp")
        self.assertEqual(serializer.validated_data["contact_person"], "Jane Doe")
        self.assertEqual(serializer.validated_data["email"], "jane@acme.test")

    def test_blank_company_name_and_contact_person_are_rejected(self):
        serializer = CustomerSerializer(data=valid_payload(company_name="   ", contact_person="  "))

        self.assertFalse(serializer.is_valid())
        self.assertIn("company_name", serializer.errors)
        self.assertIn("contact_person", serializer.errors)

    def test_field_validators_reject_whitespace_only_values(self):
        serializer = CustomerSerializer()

        with self.assertRaises(ValidationError):
            serializer.validate_company_name("   ")
        with self.assertRaises(ValidationError):
            serializer.validate_contact_person("   ")

    def test_invalid_phone_number_is_rejected(self):
        serializer = CustomerSerializer(data=valid_payload(phone_number="12"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        create_customer(email="jane@acme.test")

        serializer = CustomerSerializer(data=valid_payload(email="JANE@ACME.TEST"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_check_includes_soft_deleted_customers(self):
        create_customer(email="jane@acme.test", deleted_at=timezone.now())

        serializer = CustomerSerializer(data=valid_payload(email="jane@acme.test"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_updating_a_customer_keeping_its_own_email_is_allowed(self):
        customer = create_customer(email="jane@acme.test")

        serializer = CustomerSerializer(
            instance=customer, data=valid_payload(email="jane@acme.test"), partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
