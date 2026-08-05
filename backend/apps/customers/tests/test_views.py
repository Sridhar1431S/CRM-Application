from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.customers.models import Customer
from apps.opportunities.models import Opportunity
from tests.factories import create_admin, create_customer, create_opportunity, create_sales_rep


class CustomerViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = create_admin()
        self.rep = create_sales_rep()

    def test_list_is_paginated_and_hides_soft_deleted_customers(self):
        create_customer(company_name="Alive Co")
        deleted = create_customer()
        deleted.soft_delete()
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("customers:customer-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["company_name"], "Alive Co")

    def test_search_filters_by_company_name(self):
        create_customer(company_name="Acme Corp")
        create_customer(company_name="Globex")
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse("customers:customer-list"), {"search": "Globex"})

        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["company_name"], "Globex")

    def test_retrieve_returns_the_detail_representation(self):
        customer = create_customer(company_name="Acme Corp")
        self.client.force_authenticate(self.rep)

        response = self.client.get(reverse("customers:customer-detail", args=[customer.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["company_name"], "Acme Corp")

    def test_sales_rep_cannot_create_a_customer(self):
        self.client.force_authenticate(self.rep)

        response = self.client.post(
            reverse("customers:customer-list"),
            {
                "company_name": "Acme Corp",
                "contact_person": "Jane Doe",
                "email": "jane@acme.test",
                "phone_number": "+91 9000000001",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_delete_soft_deletes_the_customer(self):
        customer = create_customer()
        self.client.force_authenticate(self.admin)

        response = self.client.delete(
            reverse("customers:customer-detail", args=[customer.id])
        )

        self.assertEqual(response.status_code, 204)
        customer.refresh_from_db()
        self.assertIsNotNone(customer.deleted_at)
        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())

    def test_delete_is_blocked_with_422_when_open_opportunities_exist(self):
        customer = create_customer()
        create_opportunity(customer=customer, stage=Opportunity.Stage.PROPOSAL)
        self.client.force_authenticate(self.admin)

        response = self.client.delete(
            reverse("customers:customer-detail", args=[customer.id])
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["error"]["code"], "business_rule_violation")
        customer.refresh_from_db()
        self.assertIsNone(customer.deleted_at)

    def test_authentication_is_required(self):
        self.assertEqual(self.client.get(reverse("customers:customer-list")).status_code, 401)
