from django.test import TestCase

from apps.users.models import User
from apps.users.serializers import RegisterSerializer


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
