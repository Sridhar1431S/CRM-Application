from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.sales_reps.permissions import SalesRepPermission
from apps.sales_reps.serializers import SalesRepCreateSerializer, SalesRepSerializer
from apps.users.models import User
from core.pagination import StandardResultsSetPagination


class SalesRepViewSet(viewsets.ModelViewSet):
    """
    /api/sales-reps/

    CRUD is intentionally restricted to Create / Update / View / Disable --
    there is no hard delete, matching the assignment spec ("Disable" rather
    than "Delete"). This also protects referential integrity since Leads
    and Opportunities reference the rep by foreign key.
    """

    queryset = User.objects.filter(role=User.Role.SALES_REP)
    permission_classes = [SalesRepPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return SalesRepCreateSerializer
        return SalesRepSerializer

    @action(detail=True, methods=["patch"], url_path="disable")
    def disable(self, request, pk=None):
        rep = self.get_object()
        rep.is_active = False
        rep.save(update_fields=["is_active", "updated_at"])
        return Response(SalesRepSerializer(rep).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="enable")
    def enable(self, request, pk=None):
        rep = self.get_object()
        rep.is_active = True
        rep.save(update_fields=["is_active", "updated_at"])
        return Response(SalesRepSerializer(rep).data, status=status.HTTP_200_OK)
