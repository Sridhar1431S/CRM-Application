from core.permissions import RoleBasedPermission


class SalesRepPermission(RoleBasedPermission):
    """
    Only administrators manage sales representatives (create/update/disable).
    Any authenticated user may list/view reps -- sales reps need this to see
    who else exists for e.g. lead re-assignment context, and the admin
    dashboard's "active sales representatives" widget relies on it too.
    """

    admin_only_writes = True
