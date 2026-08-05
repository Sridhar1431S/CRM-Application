from rest_framework.decorators import action
from rest_framework.response import Response

from apps.opportunities.models import Opportunity
from apps.opportunities.permissions import OpportunityPermission
from apps.opportunities.serializers import OpportunitySerializer, OpportunityStageUpdateSerializer
from apps.opportunities.services import OpportunityService
from core.views import BaseModelViewSet


class OpportunityViewSet(BaseModelViewSet):
    """
    /api/opportunities/

    Sales reps only ever see their own opportunities (queryset-scoped).
    Full-object PUT/PATCH is effectively admin-only; reps must go through
    the /stage sub-action, which is the only mutation the assignment spec
    grants them ("Update Opportunity Stage").
    """

    serializer_class = OpportunitySerializer
    permission_classes = [OpportunityPermission]
    filterset_fields = ["stage", "assigned_rep", "customer"]
    search_fields = ["customer__company_name", "customer__contact_person", "assigned_rep__name"]
    ordering_fields = ["estimated_value", "expected_closing_date", "created_at", "stage"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Opportunity.objects.select_related("customer", "assigned_rep")
        return self.scope_to_assigned_rep(qs)

    @action(detail=True, methods=["patch"], url_path="stage")
    def update_stage(self, request, pk=None):
        opportunity = self.get_object()
        serializer = OpportunityStageUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        opportunity = OpportunityService.update_stage(
            opportunity, serializer.validated_data["stage"], actor=request.user
        )
        return Response(OpportunitySerializer(opportunity).data)
