from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.opportunities.permissions import OpportunityPermission
from tests.factories import create_admin, create_opportunity, create_sales_rep


class AnonymousUser:
    is_authenticated = False


class FakeView:
    def __init__(self, action=None):
        self.action = action


class OpportunityPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_admin()
        cls.rep = create_sales_rep()
        cls.other_rep = create_sales_rep()
        cls.own_opportunity = create_opportunity(assigned_rep=cls.rep)
        cls.other_opportunity = create_opportunity(assigned_rep=cls.other_rep)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = OpportunityPermission()

    def _request(self, user, method="get"):
        request = getattr(self.factory, method)("/")
        request.user = user
        return request

    def test_anonymous_user_is_denied(self):
        self.assertFalse(self.permission.has_permission(self._request(AnonymousUser()), FakeView("list")))

    def test_create_and_destroy_are_admin_only(self):
        for action in ["create", "destroy"]:
            with self.subTest(action=action):
                view = FakeView(action)
                self.assertTrue(self.permission.has_permission(self._request(self.admin, "post"), view))
                self.assertFalse(self.permission.has_permission(self._request(self.rep, "post"), view))

    def test_sales_rep_may_read_only_own_opportunity(self):
        view = FakeView("retrieve")
        self.assertTrue(
            self.permission.has_object_permission(self._request(self.rep), view, self.own_opportunity)
        )
        self.assertFalse(
            self.permission.has_object_permission(self._request(self.rep), view, self.other_opportunity)
        )

    def test_sales_rep_may_update_stage_of_own_opportunity_only(self):
        view = FakeView("update_stage")
        self.assertTrue(
            self.permission.has_object_permission(
                self._request(self.rep, "patch"), view, self.own_opportunity
            )
        )
        self.assertFalse(
            self.permission.has_object_permission(
                self._request(self.rep, "patch"), view, self.other_opportunity
            )
        )

    def test_sales_rep_cannot_update_the_full_object(self):
        view = FakeView("update")

        self.assertFalse(
            self.permission.has_object_permission(
                self._request(self.rep, "put"), view, self.own_opportunity
            )
        )

    def test_admin_has_full_object_access(self):
        view = FakeView("update")

        self.assertTrue(
            self.permission.has_object_permission(
                self._request(self.admin, "put"), view, self.other_opportunity
            )
        )
