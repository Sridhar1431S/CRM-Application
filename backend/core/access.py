def scope_to_assigned_rep(queryset, user):
    """
    Restricts a queryset of records carrying an ``assigned_rep`` FK to the
    requesting sales rep's own records. Administrators see everything.
    """
    if user.is_authenticated and user.is_sales_rep:
        return queryset.filter(assigned_rep=user)
    return queryset


def is_admin_or_assigned_rep(actor, record) -> bool:
    """True when ``actor`` is an administrator or the record's assigned rep."""
    return bool(actor.is_admin or record.assigned_rep_id == actor.id)
