from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Default pagination used across all list endpoints.

    Clients may override the page size with `?page_size=` up to `max_page_size`.
    Response envelope includes `count`, `total_pages`, `current_page`, `next`,
    `previous`, and `results` so the frontend DataTable component can render
    pagination controls without extra requests.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
