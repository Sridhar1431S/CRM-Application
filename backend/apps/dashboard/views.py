from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dashboard.services import DashboardService
from core.permissions import IsAdministrator


class AdminDashboardView(APIView):
    """GET /api/dashboard/admin"""

    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        return Response(
            {
                "summary": DashboardService.admin_summary(),
                "progress_monitoring": DashboardService.progress_monitoring(),
            }
        )


class SalesRepDashboardView(APIView):
    """GET /api/dashboard/sales-rep"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(DashboardService.sales_rep_summary(request.user))
