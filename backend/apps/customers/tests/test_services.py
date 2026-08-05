from django.test import TestCase

from apps.customers.models import Customer
from apps.customers.services import CustomerService
from apps.opportunities.models import Opportunity
from core.exceptions import BusinessRuleViolation
from tests.factories import create_customer, create_opportunity


class DeleteCustomerTests(TestCase):
    def test_customer_without_opportunities_is_soft_deleted(self):
        customer = create_customer()

        CustomerService.delete_customer(customer)

        customer.refresh_from_db()
        self.assertIsNotNone(customer.deleted_at)
        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())
        self.assertTrue(Customer.all_objects.filter(pk=customer.pk).exists())

    def test_customer_with_open_opportunity_cannot_be_deleted(self):
        customer = create_customer()
        create_opportunity(customer=customer, stage=Opportunity.Stage.NEGOTIATION)

        with self.assertRaises(BusinessRuleViolation):
            CustomerService.delete_customer(customer)

        customer.refresh_from_db()
        self.assertIsNone(customer.deleted_at)

    def test_customer_whose_opportunities_are_all_closed_can_be_deleted(self):
        customer = create_customer()
        create_opportunity(customer=customer, stage=Opportunity.Stage.WON)
        create_opportunity(customer=customer, stage=Opportunity.Stage.LOST)

        CustomerService.delete_customer(customer)

        customer.refresh_from_db()
        self.assertIsNotNone(customer.deleted_at)
