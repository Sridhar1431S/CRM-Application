from django.test import TestCase
from rest_framework.test import APIRequestFactory

from core.permissions import IsAdminOrReadOnlySalesRep, IsAdministrator, IsSalesRep
from tests.factories import create_admin, create_sales_rep


class AnonymousUser:
    is_authenticated = False


class CorePermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()

    def setUp(self):
        self.factory = APIRequestFactory()

    def _request(self, user, method="get"):
        request = getattr(self.factory, method)("/")
        request.user = user
        return request

    def test_is_administrator_allows_only_admins(self):
        permission = IsAdministrator()
        self.assertTrue(permission.has_permission(self._request(self.admin), None))
        self.assertFalse(permission.has_permission(self._request(self.rep), None))
        self.assertFalse(permission.has_permission(self._request(AnonymousUser()), None))

    def test_is_sales_rep_allows_only_sales_reps(self):
        permission = IsSalesRep()
        self.assertTrue(permission.has_permission(self._request(self.rep), None))
        self.assertFalse(permission.has_permission(self._request(self.admin), None))
        self.assertFalse(permission.has_permission(self._request(AnonymousUser()), None))

    def test_admin_or_read_only_sales_rep(self):
        permission = IsAdminOrReadOnlySalesRep()

        self.assertTrue(permission.has_permission(self._request(self.admin, "post"), None))
        self.assertTrue(permission.has_permission(self._request(self.rep, "get"), None))
        self.assertFalse(permission.has_permission(self._request(self.rep, "post"), None))
        self.assertFalse(permission.has_permission(self._request(AnonymousUser()), None))
