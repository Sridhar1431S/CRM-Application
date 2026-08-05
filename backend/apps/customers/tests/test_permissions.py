from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.customers.permissions import CustomerPermission
from tests.factories import create_admin, create_sales_rep


class AnonymousUser:
    is_authenticated = False


class CustomerPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CustomerPermission()

    def _allowed(self, user, method):
        request = getattr(self.factory, method)("/")
        request.user = user
        return self.permission.has_permission(request, None)

    def test_admin_may_read_and_write(self):
        for method in ["get", "post", "put", "patch", "delete"]:
            with self.subTest(method=method):
                self.assertTrue(self._allowed(self.admin, method))

    def test_sales_rep_may_read_but_not_write(self):
        self.assertTrue(self._allowed(self.rep, "get"))
        for method in ["post", "put", "patch", "delete"]:
            with self.subTest(method=method):
                self.assertFalse(self._allowed(self.rep, method))

    def test_anonymous_user_is_denied(self):
        self.assertFalse(self._allowed(AnonymousUser(), "get"))
