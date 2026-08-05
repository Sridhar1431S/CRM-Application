from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.sales_reps.permissions import SalesRepPermission
from tests.factories import create_admin, create_sales_rep


class AnonymousUser:
    is_authenticated = False


class SalesRepPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = SalesRepPermission()

    def _allowed(self, user, method):
        request = getattr(self.factory, method)("/")
        request.user = user
        return self.permission.has_permission(request, None)

    def test_any_authenticated_user_may_read(self):
        self.assertTrue(self._allowed(self.admin, "get"))
        self.assertTrue(self._allowed(self.rep, "get"))

    def test_only_admins_may_write(self):
        for method in ["post", "put", "patch"]:
            with self.subTest(method=method):
                self.assertTrue(self._allowed(self.admin, method))
                self.assertFalse(self._allowed(self.rep, method))

    def test_anonymous_user_is_denied(self):
        self.assertFalse(self._allowed(AnonymousUser(), "get"))
