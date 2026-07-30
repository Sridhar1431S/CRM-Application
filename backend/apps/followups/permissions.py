from rest_framework.permissions import BasePermission


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
        if request.user.is_admin:
            return True
        return obj.opportunity.assigned_rep_id == request.user.id
