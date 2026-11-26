from django.contrib import admin
from .models import ReportingAgent, SoftwareInstallation, VersionEvent

@admin.register(ReportingAgent)
class ReportingAgentAdmin(admin.ModelAdmin):
    list_display = ("hostname", "agent_id", "os_name", "os_version", "last_seen")
    search_fields = ("hostname", "agent_id", "fqdn")
    readonly_fields = ("first_seen", "last_seen")

@admin.register(SoftwareInstallation)
class SoftwareInstallationAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "category", "agent", "status", "is_present", "last_seen")
    list_filter = ("category", "status", "is_present")
    search_fields = ("name", "version", "agent__hostname")

admin.site.register(VersionEvent)
