from rest_framework.permissions import BasePermission

class CanIngestSoftwareInventory(BasePermission):
    """Require explicit plugin-model write permissions for agent ingestion."""
    message = "The API user needs add/change permissions for Software Discovery inventory."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        required = (
            "netbox_software_discovery.add_reportingagent",
            "netbox_software_discovery.change_reportingagent",
            "netbox_software_discovery.add_softwareinstallation",
            "netbox_software_discovery.change_softwareinstallation",
            "netbox_software_discovery.add_versionevent",
        )
        return user.is_superuser or user.has_perms(required)
