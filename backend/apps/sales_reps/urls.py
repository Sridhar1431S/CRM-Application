from rest_framework.routers import DefaultRouter

from apps.sales_reps.views import SalesRepViewSet

app_name = "sales_reps"

router = DefaultRouter()
router.register("", SalesRepViewSet, basename="sales-rep")

urlpatterns = router.urls
