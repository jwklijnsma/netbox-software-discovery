from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from .models import ReportingAgent, SoftwareInstallation, VersionEvent

ALLOWED_OBJECTS = {"dcim.device": ("dcim", "device"), "virtualization.virtualmachine": ("virtualization", "virtualmachine")}

def resolve_netbox_object(payload):
    """Resolve explicit NetBox object identity; optional hostname fallback is intentionally conservative."""
    from django.apps import apps
    label = str(payload.get("netbox_object_type", "")).lower()
    object_id = payload.get("netbox_object_id")
    if bool(label) != bool(object_id):
        raise ValueError("netbox_object_type and netbox_object_id must be supplied together")
    if label and object_id:
        if label not in ALLOWED_OBJECTS:
            raise ValueError("netbox_object_type must be dcim.device or virtualization.virtualmachine")
        model = apps.get_model(*ALLOWED_OBJECTS[label])
        return model.objects.filter(pk=object_id).first()
    if not settings.PLUGINS_CONFIG.get("netbox_software_discovery", {}).get("allow_auto_match", True):
        return None
    hostname = payload.get("hostname", "").split(".")[0]
    if not hostname:
        return None
    from virtualization.models import VirtualMachine
    from dcim.models import Device
    vm = VirtualMachine.objects.filter(name__iexact=hostname).first()
    return vm or Device.objects.filter(name__iexact=hostname).first()

@transaction.atomic
def ingest_report(payload):
    max_items = settings.PLUGINS_CONFIG.get("netbox_software_discovery", {}).get("max_payload_items", 10000)
    items = payload.get("software", [])
    if not isinstance(items, list) or len(items) > max_items:
        raise ValueError(f"software must be a list with at most {max_items} entries")
    required = ("agent_id", "hostname")
    if any(not payload.get(key) for key in required):
        raise ValueError("agent_id and hostname are required")
    if not isinstance(payload.get("agent_id"), str) or not isinstance(payload.get("hostname"), str):
        raise ValueError("agent_id and hostname must be strings")
    if not isinstance(payload.get("ip_addresses", []), list):
        raise ValueError("ip_addresses must be a list")
    if any(not isinstance(ip, str) for ip in payload.get("ip_addresses", [])):
        raise ValueError("ip_addresses entries must be strings")
    obj = resolve_netbox_object(payload)
    if payload.get("netbox_object_type") and payload.get("netbox_object_id") and obj is None:
        raise ValueError("The specified NetBox object does not exist")
    ct = ContentType.objects.get_for_model(obj, for_concrete_model=False) if obj else None
    agent, _ = ReportingAgent.objects.update_or_create(agent_id=str(payload["agent_id"])[:128], defaults={
        "hostname": str(payload["hostname"])[:255], "fqdn": str(payload.get("fqdn", ""))[:255],
        "os_name": str(payload.get("os_name", ""))[:128], "os_version": str(payload.get("os_version", ""))[:128],
        "architecture": str(payload.get("architecture", ""))[:64], "agent_version": str(payload.get("agent_version", ""))[:32],
        "ip_addresses": payload.get("ip_addresses", [])[:64],
        "proxmox_cluster": str(payload.get("proxmox_cluster", ""))[:128],
        "proxmox_node": str(payload.get("proxmox_node", ""))[:128], "proxmox_vmid": str(payload.get("proxmox_vmid", ""))[:32],
        "netbox_object_type": ct, "netbox_object_id": obj.pk if obj else None, "last_error": ""})
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        defaults = {"version": str(item.get("version", ""))[:255], "status": item.get("status", "unknown") if item.get("status") in dict(SoftwareInstallation.STATUS_CHOICES) else "unknown",
            "vendor": str(item.get("vendor", ""))[:255], "architecture": str(item.get("architecture", ""))[:64],
            "metadata": item.get("metadata", {}) if isinstance(item.get("metadata", {}), dict) else {},
            "image": str(item.get("image", ""))[:512],
            "is_present": True, "last_seen": timezone.now()}
        key = {"agent": agent, "name": str(item["name"])[:255],
               "category": item.get("category", "package") if item.get("category") in dict(SoftwareInstallation.CATEGORY_CHOICES) else "package",
               "source": str(item.get("source", ""))[:64]}
        installation, created = SoftwareInstallation.objects.get_or_create(**key, defaults=defaults | {"object_type": ct, "object_id": obj.pk if obj else None})
        if not created:
            old_version = installation.version
            for field, value in defaults.items(): setattr(installation, field, value)
            installation.object_type, installation.object_id = ct, obj.pk if obj else None
            installation.save()
            if old_version != installation.version:
                VersionEvent.objects.create(installation=installation, previous_version=old_version, new_version=installation.version)
        seen.add(installation.pk)
    # Mark items absent only when a complete report is explicitly declared.
    if payload.get("complete_inventory") is True:
        agent.installations.exclude(pk__in=seen).update(is_present=False)
    return agent, len(seen), obj
