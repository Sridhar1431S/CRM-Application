from django.test import TestCase

from apps.sales_reps.services import SalesRepService
from tests.factories import create_admin, create_sales_rep


class ActiveRepsCountTests(TestCase):
    def test_counts_only_active_sales_reps(self):
        create_sales_rep()
        create_sales_rep()
        create_sales_rep(is_active=False)
        create_admin()

        self.assertEqual(SalesRepService.active_reps_count(), 2)

    def test_zero_when_no_reps_exist(self):
        self.assertEqual(SalesRepService.active_reps_count(), 0)
