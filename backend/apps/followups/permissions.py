from rest_framework.permissions import BasePermission

from core.access import is_admin_or_assigned_rep


class FollowUpPermission(BasePermission):
    """
    Administrators can view all follow-ups. Sales representatives may
    create/view follow-ups only on opportunities assigned to them --
    consistent with "Only assigned representative can update opportunities"
    extending naturally to logging follow-up notes on that opportunity.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return is_admin_or_assigned_rep(request.user, obj.opportunity)
