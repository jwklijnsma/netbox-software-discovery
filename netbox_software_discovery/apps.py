from netbox.plugins import PluginConfig

class SoftwareDiscoveryConfig(PluginConfig):
    name = "netbox_software_discovery"
    verbose_name = "Software Discovery"
    description = "Agent-based software inventory and version history"
    version = "0.1.0"
    base_url = "software-discovery"
    min_version = "4.5.0"
    max_version = "4.5.99"
    required_settings = []
    default_settings = {
        "stale_after_minutes": 60,
        "allow_auto_match": True,
        "max_payload_items": 10000,
    }

config = SoftwareDiscoveryConfig
