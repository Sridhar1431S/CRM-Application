from rest_framework.permissions import SAFE_METHODS, BasePermission


class LeadPermission(BasePermission):
    """
    Administrators have full CRUD + assign/convert. Sales representatives
    may view leads (scoped to their own assignments by the queryset in the
    ViewSet) and update status/notes on their own leads, but may not
    create, delete, assign, or convert -- those are administrator actions
    per the assignment spec.
    """

    ADMIN_ONLY_ACTIONS = {"create", "destroy", "assign", "convert"}

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if getattr(view, "action", None) in self.ADMIN_ONLY_ACTIONS:
            return request.user.is_admin
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if request.method in SAFE_METHODS:
            return obj.assigned_rep_id == request.user.id
        # Sales reps may only update (status/notes) their own leads.
        return obj.assigned_rep_id == request.user.id
