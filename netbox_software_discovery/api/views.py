from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import ReportingAgent, SoftwareInstallation, VersionEvent
from .serializers import AgentSerializer, SoftwareSerializer, VersionEventSerializer
from ..services import ingest_report
from ..permissions import CanIngestSoftwareInventory

class IngestView(APIView):
    permission_classes = [IsAuthenticated, CanIngestSoftwareInventory]
    def post(self, request):
        if not isinstance(request.data, dict):
            return Response({"detail": "Request body must be a JSON object"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            agent, count, obj = ingest_report(request.data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"agent_id": agent.agent_id, "hostname": agent.hostname, "accepted": count,
                         "matched_object": str(obj) if obj else None}, status=status.HTTP_200_OK)

class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportingAgent.objects.all().prefetch_related("installations")
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

class SoftwareViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SoftwareInstallation.objects.select_related("agent", "object_type")
    serializer_class = SoftwareSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["name", "version", "category", "status", "is_present", "agent"]

class VersionEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = VersionEvent.objects.select_related("installation", "installation__agent")
    serializer_class = VersionEventSerializer
    permission_classes = [IsAuthenticated]
