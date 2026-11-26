import os
from dataclasses import dataclass

def _bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")

@dataclass
class Config:
    netbox_url: str = os.getenv("NETBOX_URL", "").rstrip("/")
    netbox_token: str = os.getenv("NETBOX_TOKEN", "")
    agent_id: str = os.getenv("AGENT_ID", "")
    interval: int = int(os.getenv("DISCOVERY_INTERVAL", "900"))
    verify_tls: bool = _bool("NETBOX_VERIFY_TLS", True)
    timeout: int = int(os.getenv("NETBOX_TIMEOUT", "30"))
    netbox_object_type: str = os.getenv("NETBOX_OBJECT_TYPE", "")
    netbox_object_id: str = os.getenv("NETBOX_OBJECT_ID", "")
    proxmox_cluster: str = os.getenv("PROXMOX_CLUSTER", "")
    proxmox_node: str = os.getenv("PROXMOX_NODE", "")
    proxmox_vmid: str = os.getenv("PROXMOX_VMID", "")
    include_packages: bool = _bool("DISCOVER_PACKAGES", True)
    include_services: bool = _bool("DISCOVER_SERVICES", True)
    include_containers: bool = _bool("DISCOVER_CONTAINERS", True)
    include_kubernetes: bool = _bool("DISCOVER_KUBERNETES", True)
    complete_inventory: bool = _bool("COMPLETE_INVENTORY", False)
