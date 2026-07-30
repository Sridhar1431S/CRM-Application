from rest_framework.permissions import SAFE_METHODS, BasePermission


class OpportunityPermission(BasePermission):
    """
    Administrators: full CRUD.
    Sales representatives: may view opportunities assigned to them
    (queryset-scoped) and update only the stage of their own opportunities
    via the dedicated /stage action -- never create or delete, and never
    touch another rep's opportunity ("Only assigned representative can
    update opportunities" per the assignment spec).
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if getattr(view, "action", None) in {"create", "destroy"}:
            return request.user.is_admin
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if request.method in SAFE_METHODS:
            return obj.assigned_rep_id == request.user.id
        if getattr(view, "action", None) == "update_stage":
            return obj.assigned_rep_id == request.user.id
        # Sales reps cannot PUT/PATCH the full object directly, only via /stage.
        return False
