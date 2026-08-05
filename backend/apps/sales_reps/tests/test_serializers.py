from django.test import TestCase

from apps.sales_reps.serializers import SalesRepCreateSerializer, SalesRepSerializer
from apps.users.models import User
from tests.factories import create_sales_rep


def valid_payload(**overrides):
    payload = {
        "name": "Priya Sharma",
        "email": "  Priya@Crmlite.TEST ",
        "password": "Str0ng!Passw0rd",
        "is_active": True,
    }
    payload.update(overrides)
    return payload


class SalesRepCreateSerializerTests(TestCase):
    def test_creates_a_sales_rep_with_a_hashed_password(self):
        serializer = SalesRepCreateSerializer(data=valid_payload())

        self.assertTrue(serializer.is_valid(), serializer.errors)
        rep = serializer.save()

        self.assertEqual(rep.email, "priya@crmlite.test")
        self.assertEqual(rep.role, User.Role.SALES_REP)
        self.assertNotEqual(rep.password, "Str0ng!Passw0rd")
        self.assertTrue(rep.check_password("Str0ng!Passw0rd"))

    def test_duplicate_email_is_rejected_case_insensitively(self):
        create_sales_rep(email="priya@crmlite.test")

        serializer = SalesRepCreateSerializer(data=valid_payload(email="PRIYA@CRMLITE.TEST"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_weak_password_is_rejected_by_django_validators(self):
        serializer = SalesRepCreateSerializer(data=valid_payload(password="123"))

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_password_is_never_exposed_in_the_representation(self):
        serializer = SalesRepCreateSerializer(data=valid_payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        self.assertNotIn("password", serializer.data)


class SalesRepSerializerTests(TestCase):
    def test_role_is_read_only(self):
        rep = create_sales_rep()

        serializer = SalesRepSerializer(
            instance=rep, data={"role": User.Role.ADMIN, "name": "Renamed"}, partial=True
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.role, User.Role.SALES_REP)
        self.assertEqual(updated.name, "Renamed")

    def test_exposes_status_via_is_active(self):
        rep = create_sales_rep(is_active=False)

        self.assertFalse(SalesRepSerializer(rep).data["is_active"])
