from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.followups.models import FollowUp
from apps.followups.serializers import FollowUpSerializer
from apps.followups.services import FollowUpService
from apps.opportunities.models import Opportunity
from core.access import scope_to_assigned_rep
from core.pagination import StandardResultsSetPagination


def _get_visible_opportunity(request, opportunity_id):
    qs = scope_to_assigned_rep(Opportunity.objects.all(), request.user)
    try:
        return qs.get(pk=opportunity_id)
    except Opportunity.DoesNotExist:
        raise NotFound("Opportunity not found.")


class OpportunityFollowUpListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/opportunities/{opportunity_id}/followups  -- view history
    POST /api/opportunities/{opportunity_id}/followups  -- create
    """

    serializer_class = FollowUpSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        opportunity = _get_visible_opportunity(self.request, self.kwargs["opportunity_id"])
        return FollowUp.objects.filter(opportunity=opportunity).select_related("created_by")

    def create(self, request, *args, **kwargs):
        opportunity = _get_visible_opportunity(request, self.kwargs["opportunity_id"])
        serializer = FollowUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        followup = FollowUpService.create_followup(
            opportunity,
            note=serializer.validated_data["note"],
            next_followup_date=serializer.validated_data.get("next_followup_date"),
            actor=request.user,
        )
        return Response(FollowUpSerializer(followup).data, status=201)


class UpcomingFollowUpsView(APIView):
    """
    GET /api/followups/upcoming

    Powers "Today's Follow-Ups" / "Upcoming Follow-Ups" widgets. Admins see
    every upcoming follow-up; sales reps see only their own.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = FollowUp.objects.filter(
            next_followup_date__isnull=False, next_followup_date__gte=timezone.localdate()
        ).select_related("opportunity", "opportunity__customer", "created_by")

        if request.user.is_sales_rep:
            qs = qs.filter(opportunity__assigned_rep=request.user)

        qs = qs.order_by("next_followup_date")[:50]
        return Response(FollowUpSerializer(qs, many=True).data)
