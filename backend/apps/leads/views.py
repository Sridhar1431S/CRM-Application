from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.leads.models import Lead
from apps.leads.permissions import LeadPermission
from apps.leads.serializers import LeadAssignSerializer, LeadSerializer
from apps.leads.services import LeadService
from apps.opportunities.serializers import OpportunitySerializer
from core.views import BaseModelViewSet


class LeadViewSet(BaseModelViewSet):
    """
    /api/leads/

    Sales reps only ever see leads assigned to them (enforced in
    get_queryset, not just permissions, so it also drives correct
    pagination counts and prevents ID-guessing enumeration of other
    reps' leads via the list endpoint).
    """

    serializer_class = LeadSerializer
    permission_classes = [LeadPermission]
    filterset_fields = ["status", "priority", "assigned_rep"]
    search_fields = ["company_name", "contact_name", "email", "assigned_rep__name"]
    ordering_fields = ["company_name", "created_at", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Lead.objects.filter(deleted_at__isnull=True).select_related("assigned_rep")
        return self.scope_to_assigned_rep(qs)

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at", "updated_at"])

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        lead = self.get_object()
        serializer = LeadAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = LeadService.assign(lead, serializer.validated_data["assigned_rep"])
        return Response(LeadSerializer(lead).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="convert")
    def convert(self, request, pk=None):
        lead = self.get_object()
        estimated_value = request.data.get("estimated_value")
        expected_closing_date = request.data.get("expected_closing_date")

        if estimated_value is None or expected_closing_date is None:
            return Response(
                {"detail": "estimated_value and expected_closing_date are required to convert a lead."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        opportunity = LeadService.convert_to_opportunity(
            lead,
            estimated_value=estimated_value,
            expected_closing_date=expected_closing_date,
            actor=request.user,
        )
        return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_201_CREATED)
