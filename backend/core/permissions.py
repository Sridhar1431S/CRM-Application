from rest_framework.permissions import BasePermission, SAFE_METHODS


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


class IsAdminOrReadOnlySalesRep(BasePermission):
    """
    Administrators have full access. Sales representatives may only read
    (GET/HEAD/OPTIONS). Used on resources that sales reps can view but not
    mutate directly (e.g. the Customers list, other reps' records).
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.role == request.user.Role.ADMIN:
            return True
        return request.method in SAFE_METHODS
