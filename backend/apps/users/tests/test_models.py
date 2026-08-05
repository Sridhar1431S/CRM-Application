from django.test import TestCase

from apps.users.models import User


class UserManagerTests(TestCase):
    def test_create_user_defaults_to_sales_rep_without_staff_access(self):
        user = User.objects.create_user(email="rep@crmlite.test", password="Rep@12345", name="Priya")

        self.assertEqual(user.role, User.Role.SALES_REP)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("Rep@12345"))

    def test_create_user_normalizes_the_email_domain(self):
        user = User.objects.create_user(email="Rep@CRMLITE.TEST", password="Rep@12345", name="Priya")

        self.assertEqual(user.email, "Rep@crmlite.test")

    def test_create_user_requires_an_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="Rep@12345", name="Priya")

    def test_create_superuser_is_an_admin_with_staff_access(self):
        user = User.objects.create_superuser(
            email="admin@crmlite.test", password="Admin@12345", name="Alex"
        )

        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_rejects_downgraded_flags(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin2@crmlite.test", password="Admin@12345", name="Alex", is_staff=False
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin3@crmlite.test", password="Admin@12345", name="Alex", is_superuser=False
            )


class UserModelTests(TestCase):
    def test_str_shows_name_and_email(self):
        user = User.objects.create_user(email="rep@crmlite.test", password="Rep@12345", name="Priya")

        self.assertEqual(str(user), "Priya <rep@crmlite.test>")

    def test_role_properties(self):
        admin = User.objects.create_superuser(
            email="admin@crmlite.test", password="Admin@12345", name="Alex"
        )
        rep = User.objects.create_user(email="rep@crmlite.test", password="Rep@12345", name="Priya")

        self.assertTrue(admin.is_admin)
        self.assertFalse(admin.is_sales_rep)
        self.assertTrue(rep.is_sales_rep)
        self.assertFalse(rep.is_admin)
