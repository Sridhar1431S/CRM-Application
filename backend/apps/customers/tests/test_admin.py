from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from apps.customers.admin import CustomerAdmin
from apps.customers.models import Customer
from tests.factories import create_customer


class CustomerAdminTests(TestCase):
    def test_admin_queryset_includes_soft_deleted_customers(self):
        alive = create_customer()
        deleted = create_customer()
        deleted.soft_delete()

        queryset = CustomerAdmin(Customer, AdminSite()).get_queryset(request=None)

        self.assertEqual(set(queryset), {alive, deleted})
