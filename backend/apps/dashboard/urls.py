from django.urls import path

from apps.dashboard.views import AdminDashboardView, SalesRepDashboardView

app_name = "dashboard"

urlpatterns = [
    path("admin", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("sales-rep", SalesRepDashboardView.as_view(), name="sales-rep-dashboard"),
]
