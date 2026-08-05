from core.permissions import AssignedRepObjectPermissionMixin, RoleBasedPermission


class OpportunityPermission(AssignedRepObjectPermissionMixin, RoleBasedPermission):
    """
    Administrators: full CRUD.
    Sales representatives: may view opportunities assigned to them
    (queryset-scoped) and update only the stage of their own opportunities
    via the dedicated /stage action -- never create or delete, and never
    touch another rep's opportunity ("Only assigned representative can
    update opportunities" per the assignment spec).
    """

    admin_only_actions = frozenset({"create", "destroy"})

    def has_write_object_permission(self, request, view, obj):
        # Sales reps cannot PUT/PATCH the full object directly, only via /stage.
        if getattr(view, "action", None) != "update_stage":
            return False
        return obj.assigned_rep_id == request.user.id
