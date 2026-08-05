from core.permissions import AssignedRepObjectPermissionMixin, RoleBasedPermission


class LeadPermission(AssignedRepObjectPermissionMixin, RoleBasedPermission):
    """
    Administrators have full CRUD + assign/convert. Sales representatives
    may view leads (scoped to their own assignments by the queryset in the
    ViewSet) and update status/notes on their own leads, but may not
    create, delete, assign, or convert -- those are administrator actions
    per the assignment spec.
    """

    admin_only_actions = frozenset({"create", "destroy", "assign", "convert"})

    def has_write_object_permission(self, request, view, obj):
        # Sales reps may only update (status/notes) their own leads.
        return obj.assigned_rep_id == request.user.id
