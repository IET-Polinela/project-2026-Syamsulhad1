from rest_framework.routers import DefaultRouter
from .api_views import ReportViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'report', ReportViewSet, basename='report-legacy')

urlpatterns = router.urls
