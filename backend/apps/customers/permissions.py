from core.permissions import RoleBasedPermission


class CustomerPermission(RoleBasedPermission):
    """
    Per the assignment: "Administrators should be able to Create/Edit/Delete/
    View customers." Sales representatives can view customers (they need
    this to work leads/opportunities tied to a customer) but not mutate them.
    """

    admin_only_writes = True
