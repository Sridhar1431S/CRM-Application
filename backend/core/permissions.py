from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.access import is_admin_or_assigned_rep


class RoleBasedPermission(BasePermission):
    """
    Base class for the resource permissions: anonymous requests are always
    rejected, then the declarative role rules below are applied. Subclasses
    set only what differs instead of repeating the authentication and
    administrator checks.

      * ``admin_only_actions`` -- ViewSet actions restricted to administrators.
      * ``admin_only_writes``  -- when true, non-administrators are read-only.
    """

    admin_only_actions: frozenset = frozenset()
    admin_only_writes = False

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if getattr(view, "action", None) in self.admin_only_actions:
            return request.user.is_admin
        if self.admin_only_writes and request.method not in SAFE_METHODS:
            return request.user.is_admin
        return True


class AssignedRepObjectPermissionMixin:
    """
    Object-level rules for records that carry an ``assigned_rep`` FK:
    administrators always pass, everyone else may only read their own
    records. Writes fall through to ``has_write_object_permission``, which
    denies by default so each resource opts in explicitly.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if request.method in SAFE_METHODS:
            return is_admin_or_assigned_rep(request.user, obj)
        return self.has_write_object_permission(request, view, obj)

    def has_write_object_permission(self, request, view, obj):
        return False


class IsAdministrator(BasePermission):
    """Allows access only to users with the Administrator role."""

    message = "Only administrators may perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )


class IsSalesRep(BasePermission):
    """Allows access only to users with the Sales Representative role."""

    message = "Only sales representatives may perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.SALES_REP
        )


class IsAdminOrReadOnlySalesRep(RoleBasedPermission):
    """
    Administrators have full access. Sales representatives may only read
    (GET/HEAD/OPTIONS). Used on resources that sales reps can view but not
    mutate directly (e.g. the Customers list, other reps' records).
    """

    admin_only_writes = True
