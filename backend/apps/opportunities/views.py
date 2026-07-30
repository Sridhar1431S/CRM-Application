from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.opportunities.models import Opportunity
from apps.opportunities.permissions import OpportunityPermission
from apps.opportunities.serializers import OpportunitySerializer, OpportunityStageUpdateSerializer
from apps.opportunities.services import OpportunityService
from core.pagination import StandardResultsSetPagination


class OpportunityViewSet(viewsets.ModelViewSet):
    """
    /api/opportunities/

    Sales reps only ever see their own opportunities (queryset-scoped).
    Full-object PUT/PATCH is effectively admin-only; reps must go through
    the /stage sub-action, which is the only mutation the assignment spec
    grants them ("Update Opportunity Stage").
    """

    serializer_class = OpportunitySerializer
    permission_classes = [OpportunityPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["stage", "assigned_rep", "customer"]
    search_fields = ["customer__company_name", "customer__contact_person", "assigned_rep__name"]
    ordering_fields = ["estimated_value", "expected_closing_date", "created_at", "stage"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Opportunity.objects.select_related("customer", "assigned_rep")
        user = self.request.user
        if user.is_authenticated and user.is_sales_rep:
            return qs.filter(assigned_rep=user)
        return qs

    @action(detail=True, methods=["patch"], url_path="stage")
    def update_stage(self, request, pk=None):
        opportunity = self.get_object()
        serializer = OpportunityStageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        opportunity = OpportunityService.update_stage(
            opportunity, serializer.validated_data["stage"], actor=request.user
        )
        return Response(OpportunitySerializer(opportunity).data)
