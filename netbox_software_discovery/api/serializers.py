from rest_framework import serializers
from .models import ReportingAgent, SoftwareInstallation, VersionEvent

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingAgent
        fields = "__all__"
        read_only_fields = ("id", "first_seen", "last_seen")

class SoftwareSerializer(serializers.ModelSerializer):
    hostname = serializers.CharField(source="agent.hostname", read_only=True)
    class Meta:
        model = SoftwareInstallation
        fields = "__all__"
        read_only_fields = ("id", "first_seen", "last_seen", "agent", "object_type", "object_id")

class VersionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionEvent
        fields = "__all__"
        read_only_fields = ("id", "observed_at")
