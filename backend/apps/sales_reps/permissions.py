from rest_framework.permissions import SAFE_METHODS, BasePermission


class SalesRepPermission(BasePermission):
    """
    Only administrators manage sales representatives (create/update/disable).
    Any authenticated user may list/view reps -- sales reps need this to see
    who else exists for e.g. lead re-assignment context, and the admin
    dashboard's "active sales representatives" widget relies on it too.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin
