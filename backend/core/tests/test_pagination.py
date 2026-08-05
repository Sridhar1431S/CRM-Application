from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.customers.models import Customer
from core.pagination import StandardResultsSetPagination
from tests.factories import create_customer


class StandardResultsSetPaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for _ in range(3):
            create_customer()

    def setUp(self):
        self.paginator = StandardResultsSetPagination()
        self.factory = APIRequestFactory()

    def test_envelope_exposes_count_total_pages_and_current_page(self):
        request = Request(self.factory.get("/?page_size=2"))
        page = self.paginator.paginate_queryset(Customer.objects.all(), request)

        response = self.paginator.get_paginated_response([{"id": str(obj.id)} for obj in page])

        self.assertEqual(response.data["count"], 3)
        self.assertEqual(response.data["total_pages"], 2)
        self.assertEqual(response.data["current_page"], 1)
        self.assertIsNone(response.data["previous"])
        self.assertIsNotNone(response.data["next"])
        self.assertEqual(len(response.data["results"]), 2)

    def test_page_size_query_param_is_capped_at_max_page_size(self):
        request = Request(self.factory.get("/?page_size=500"))

        self.assertEqual(
            self.paginator.get_page_size(request),
            StandardResultsSetPagination.max_page_size,
        )
