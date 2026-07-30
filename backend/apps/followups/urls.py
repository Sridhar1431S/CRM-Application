from django.urls import path

from apps.followups.views import OpportunityFollowUpListCreateView, UpcomingFollowUpsView

app_name = "followups"

# Included twice from config/urls.py:
#   /api/opportunities/<uuid>/followups   (nested, matches assignment's REST spec)
#   /api/followups/upcoming               (top-level, for dashboard/sales workspace)
nested_urlpatterns = [
    path("<uuid:opportunity_id>/followups", OpportunityFollowUpListCreateView.as_view(), name="opportunity-followups"),
]

urlpatterns = [
    path("upcoming", UpcomingFollowUpsView.as_view(), name="upcoming-followups"),
]
