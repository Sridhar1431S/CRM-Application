from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.users.models import User
from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from tests.factories import create_sales_rep


class RegisterSerializerTests(TestCase):
    def test_register_serializer_creates_sales_rep_user(self):
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password123!",
            "password_confirm": "Password123!",
            "role": User.Role.SALES_REP,
        }

        serializer = RegisterSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, User.Role.SALES_REP)
        self.assertTrue(user.check_password("Password123!"))

    def test_register_serializer_requires_matching_passwords(self):
        data = {
            "name": "Test User",
            "email": "test2@example.com",
            "password": "Password123!",
            "password_confirm": "Different123!",
            "role": User.Role.SALES_REP,
        }

        serializer = RegisterSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_register_serializer_rejects_an_existing_email_case_insensitively(self):
        create_sales_rep(email="taken@example.com")

        serializer = RegisterSerializer(
            data={
                "name": "Test User",
                "email": "TAKEN@example.com",
                "password": "Password123!",
                "password_confirm": "Password123!",
                "role": User.Role.SALES_REP,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class LoginSerializerTests(TestCase):
    def setUp(self):
        self.rep = create_sales_rep(email="priya@crmlite.test", password="Rep@12345")

    def _serializer(self, **overrides):
        data = {"email": self.rep.email, "password": "Rep@12345"}
        data.update(overrides)
        return LoginSerializer(data=data)

    def test_valid_credentials_return_tokens_and_user_payload(self):
        serializer = self._serializer()

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertIn("access", serializer.validated_data)
        self.assertIn("refresh", serializer.validated_data)
        self.assertEqual(serializer.validated_data["user"]["email"], self.rep.email)
        self.assertEqual(serializer.validated_data["user"]["role"], User.Role.SALES_REP)

    def test_wrong_password_is_rejected(self):
        serializer = self._serializer(password="wrong-password")

        with self.assertRaises(ValidationError) as ctx:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Invalid email or password.", str(ctx.exception.detail))

    def test_unknown_email_is_rejected(self):
        serializer = self._serializer(email="nobody@crmlite.test")

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_disabled_account_cannot_log_in(self):
        self.rep.is_active = False
        self.rep.save(update_fields=["is_active"])

        serializer = self._serializer()

        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class UserSerializerTests(TestCase):
    def test_exposes_read_only_profile_fields(self):
        rep = create_sales_rep(name="Priya Sharma")

        data = UserSerializer(rep).data

        self.assertEqual(
            set(data), {"id", "name", "email", "role", "is_active", "created_at"}
        )
        self.assertEqual(data["name"], "Priya Sharma")
