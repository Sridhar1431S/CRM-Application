from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.followups.permissions import FollowUpPermission
from tests.factories import create_admin, create_followup, create_opportunity, create_sales_rep


class AnonymousUser:
    is_authenticated = False


class FollowUpPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()
        cls.other_rep = create_sales_rep()
        cls.followup = create_followup(opportunity=create_opportunity(assigned_rep=cls.rep))

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = FollowUpPermission()

    def _request(self, user, method="get"):
        request = getattr(self.factory, method)("/")
        request.user = user
        return request

    def test_authentication_is_required(self):
        self.assertTrue(self.permission.has_permission(self._request(self.rep), None))
        self.assertFalse(self.permission.has_permission(self._request(AnonymousUser()), None))

    def test_admin_may_access_any_followup(self):
        self.assertTrue(self.permission.has_object_permission(self._request(self.admin), None, self.followup))

    def test_rep_may_access_only_followups_on_own_opportunities(self):
        self.assertTrue(self.permission.has_object_permission(self._request(self.rep), None, self.followup))
        self.assertFalse(
            self.permission.has_object_permission(self._request(self.other_rep), None, self.followup)
        )
