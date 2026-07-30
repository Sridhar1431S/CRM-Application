from rest_framework.routers import DefaultRouter

from apps.opportunities.views import OpportunityViewSet

app_name = "opportunities"

router = DefaultRouter()
router.register("", OpportunityViewSet, basename="opportunity")

urlpatterns = router.urls
