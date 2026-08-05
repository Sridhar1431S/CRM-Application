from rest_framework import status
from rest_framework.response import Response

from apps.customers.models import Customer
from apps.customers.permissions import CustomerPermission
from apps.customers.serializers import CustomerListSerializer, CustomerSerializer
from apps.customers.services import CustomerService
from core.views import BaseModelViewSet


class CustomerViewSet(BaseModelViewSet):
    """
    /api/customers/

    Supports search (?search=), status filtering (?status=active), and
    ordering (?ordering=-created_at or ?ordering=company_name), plus the
    standard paginated list envelope.
    """

    queryset = Customer.objects.all()
    permission_classes = [CustomerPermission]
    filterset_fields = ["status"]
    search_fields = ["company_name", "contact_person", "email"]
    ordering_fields = ["company_name", "created_at", "status"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        return CustomerSerializer

    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()
        CustomerService.delete_customer(customer)
        return Response(status=status.HTTP_204_NO_CONTENT)
