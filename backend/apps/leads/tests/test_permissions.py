from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.leads.permissions import LeadPermission
from tests.factories import create_admin, create_lead, create_sales_rep


class AnonymousUser:
    is_authenticated = False


class FakeView:
    def __init__(self, action=None):
        self.action = action


class LeadPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()
        cls.other_rep = create_sales_rep()
        cls.own_lead = create_lead(assigned_rep=cls.rep)
        cls.other_lead = create_lead(assigned_rep=cls.other_rep)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = LeadPermission()

    def _request(self, user, method="get"):
        request = getattr(self.factory, method)("/")
        request.user = user
        return request

    def test_anonymous_user_is_denied(self):
        self.assertFalse(self.permission.has_permission(self._request(AnonymousUser()), FakeView("list")))

    def test_admin_only_actions_are_denied_to_sales_reps(self):
        for action in LeadPermission.ADMIN_ONLY_ACTIONS:
            with self.subTest(action=action):
                view = FakeView(action)
                self.assertTrue(self.permission.has_permission(self._request(self.admin, "post"), view))
                self.assertFalse(self.permission.has_permission(self._request(self.rep, "post"), view))

    def test_sales_rep_may_list_and_retrieve(self):
        self.assertTrue(self.permission.has_permission(self._request(self.rep), FakeView("list")))

    def test_sales_rep_object_access_limited_to_own_leads(self):
        view = FakeView("retrieve")
        self.assertTrue(
            self.permission.has_object_permission(self._request(self.rep), view, self.own_lead)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(self.rep), view, self.other_lead)
        )

    def test_sales_rep_may_update_only_own_lead(self):
        view = FakeView("partial_update")
        self.assertTrue(
            self.permission.has_object_permission(self._request(self.rep, "patch"), view, self.own_lead)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(self.rep, "patch"), view, self.other_lead)
        )

    def test_admin_has_object_access_to_any_lead(self):
        view = FakeView("partial_update")
        self.assertTrue(
            self.permission.has_object_permission(self._request(self.admin, "patch"), view, self.other_lead)
        )
