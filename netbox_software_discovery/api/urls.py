from django.urls import path
from netbox.api.routers import NetBoxRouter
from .views import AgentViewSet, SoftwareViewSet, VersionEventViewSet, IngestView

router = NetBoxRouter()
router.register("agents", AgentViewSet)
router.register("software", SoftwareViewSet)
router.register("version-events", VersionEventViewSet)
urlpatterns = [path("ingest/", IngestView.as_view(), name="software-discovery-ingest"), *router.urls]
