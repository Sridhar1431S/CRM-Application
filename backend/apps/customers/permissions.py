from rest_framework.permissions import SAFE_METHODS, BasePermission


class CustomerPermission(BasePermission):
    """
    Per the assignment: "Administrators should be able to Create/Edit/Delete/
    View customers." Sales representatives can view customers (they need
    this to work leads/opportunities tied to a customer) but not mutate them.
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin
