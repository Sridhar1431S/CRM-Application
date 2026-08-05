from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from tests.factories import create_customer


class CustomerModelTests(TestCase):
    def test_str_is_company_name(self):
        customer = create_customer(company_name="Acme Corp")

        self.assertEqual(str(customer), "Acme Corp")

    def test_default_manager_hides_soft_deleted_rows(self):
        alive = create_customer()
        deleted = create_customer(deleted_at=timezone.now())

        self.assertEqual(list(Customer.objects.all()), [alive])
        self.assertEqual(set(Customer.all_objects.all()), {alive, deleted})

    def test_soft_delete_sets_deleted_at(self):
        customer = create_customer()

        customer.soft_delete()

        customer.refresh_from_db()
        self.assertIsNotNone(customer.deleted_at)

    def test_status_defaults_to_prospect(self):
        self.assertEqual(create_customer().status, Customer.Status.PROSPECT)
