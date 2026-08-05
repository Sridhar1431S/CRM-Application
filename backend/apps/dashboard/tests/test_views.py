from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import create_admin, create_opportunity, create_sales_rep


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()

    def test_admin_dashboard_returns_summary_and_progress_table(self):
        create_opportunity(assigned_rep=self.rep)
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse("dashboard:admin-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["open_opportunities"], 1)
        self.assertEqual(len(response.data["progress_monitoring"]), 1)

    def test_admin_dashboard_is_forbidden_for_sales_reps(self):
        self.client.force_authenticate(self.rep)

        self.assertEqual(self.client.get(reverse("dashboard:admin-dashboard")).status_code, 403)

    def test_sales_rep_dashboard_is_scoped_to_the_caller(self):
        create_opportunity(assigned_rep=self.rep)
        create_opportunity(assigned_rep=create_sales_rep())
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("dashboard:sales-rep-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["open_opportunities"], 1)
        self.assertEqual(response.data["assigned_customers"], 1)

    def test_dashboards_require_authentication(self):
        self.assertEqual(self.client.get(reverse("dashboard:admin-dashboard")).status_code, 401)
        self.assertEqual(self.client.get(reverse("dashboard:sales-rep-dashboard")).status_code, 401)
