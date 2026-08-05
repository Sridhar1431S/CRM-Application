from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from core.access import scope_to_assigned_rep
from core.pagination import StandardResultsSetPagination


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Shared list plumbing for the CRM resources: the standard paginated list
    envelope plus filtering, search, and ordering backends. Subclasses declare
    only the fields those backends operate on.
    """

    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def scope_to_assigned_rep(self, queryset):
        """
        Restricts a queryset to the requesting sales rep's own records.
        Applied in ``get_queryset`` (rather than only in permissions) so that
        pagination counts are correct and other reps' records cannot be
        enumerated by guessing IDs.
        """
        return scope_to_assigned_rep(queryset, self.request.user)
