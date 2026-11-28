# API

All endpoints require NetBox authentication. Use a scoped service token.

- `POST /api/plugins/software-discovery/ingest/` — agent report.
- `GET /api/plugins/software-discovery/api/agents/` — reporting agents.
- `GET /api/plugins/software-discovery/api/software/` — installations. Supports standard DRF filters for `name`, `version`, `category`, `status`, `is_present`, `agent`.
- `GET /api/plugins/software-discovery/api/version-events/` — version history.

Example payload:

```json
{
  "agent_id": "web01.example.org",
  "hostname": "web01",
  "os_name": "Ubuntu 24.04.3 LTS",
  "os_version": "24.04",
  "architecture": "x86_64",
  "agent_version": "0.1.0",
  "netbox_object_type": "virtualization.virtualmachine",
  "netbox_object_id": 123,
  "proxmox_cluster": "homelab",
  "proxmox_node": "pve01",
  "proxmox_vmid": "101",
  "complete_inventory": true,
  "software": [
    {"name": "nginx", "version": "1.26.3", "category": "package", "source": "dpkg", "status": "installed"},
    {"name": "nginx", "version": "1.26.3", "category": "service", "source": "systemd", "status": "running"},
    {"name": "frontend", "version": "2026.11", "category": "container", "source": "docker", "image": "registry.example.org/frontend:2026.11", "status": "running"}
  ]
}
```

A report only marks prior records absent if `complete_inventory: true`. The agent defaults this to `false` (`COMPLETE_INVENTORY=false`) because collectors are best-effort; enable it only after validating all configured collectors and their permissions, otherwise a transient collector failure could incorrectly mark software absent.
