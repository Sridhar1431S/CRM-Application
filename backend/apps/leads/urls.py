from rest_framework.routers import DefaultRouter

from apps.leads.views import LeadViewSet

app_name = "leads"

router = DefaultRouter()
router.register("", LeadViewSet, basename="lead")

urlpatterns = router.urls
