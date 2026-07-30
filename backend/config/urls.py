from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from apps.followups.urls import nested_urlpatterns as followup_nested_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="CRM Lite API",
        default_version="v1",
        description="REST API for the CRM Lite take-home assignment (Tika).",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/", include("apps.users.urls")),
    # Core resources
    path("api/customers/", include("apps.customers.urls")),
    path("api/sales-reps/", include("apps.sales_reps.urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("api/opportunities/", include("apps.opportunities.urls")),
    # Follow-ups: nested under opportunities (POST/GET history) + top-level "upcoming"
    path("api/opportunities/", include((followup_nested_urlpatterns, "opportunity-followups"))),
    path("api/followups/", include("apps.followups.urls")),
    # Dashboard
    path("api/dashboard/", include("apps.dashboard.urls")),
    # API docs
    path("api/docs/swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
