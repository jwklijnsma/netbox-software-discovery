# NetBox Software Discovery

Agent-based software inventory for **NetBox 4.5.x**. A small Python agent inventories its local operating system, installed packages, services, Docker/Podman containers and (when `kubectl` is available) Kubernetes pod containers. It sends a report to a NetBox plugin over HTTPS.

## Features in 0.1.0

- NetBox plugin models for reporting agents, software installations and version-change events.
- Authenticated ingest endpoint: `POST /api/plugins/software-discovery/ingest/`.
- Read-only REST endpoints under `/api/plugins/software-discovery/api/`.
- UI inventory and reporting-agent pages under `/plugins/software-discovery/`.
- Linux package discovery via dpkg, RPM or APK; Windows installed software via uninstall registry keys.
- systemd and Windows service state; Docker and Podman containers; Kubernetes pods via kubectl.
- Explicit NetBox object binding (`NETBOX_OBJECT_TYPE` + `NETBOX_OBJECT_ID`) or conservative hostname matching.
- Optional Proxmox VM metadata (`PROXMOX_CLUSTER`, `PROXMOX_NODE`, `PROXMOX_VMID`) so guest agents can be reconciled with Proxmox inventory.
- Version change history and complete-inventory stale marking.

> Scope note: Proxmox is the virtualization layer, not a guest package manager. Install the agent inside each guest VM/LXC. Set the optional Proxmox metadata variables to record the VMID/node/cluster. A future host-side Proxmox API collector can enrich guest-to-NetBox mapping; this release does not query the Proxmox API or automatically create NetBox VMs.

## Requirements

- NetBox 4.5.x and Python 3.12+ on the NetBox application environment.
- Python 3.12+ on Linux/Windows agent hosts.
- Agent outbound connectivity to NetBox HTTPS.
- For Kubernetes discovery, `kubectl` installed and configured with read-only permissions to list pods across the namespaces you want inventoried.
- For Docker/Podman discovery, the agent user needs permission to query the respective engine socket.

## Install the NetBox plugin

Install the package into the same Python environment used by NetBox (or bake it into your NetBox image):

```bash
python -m pip install .
```

Add the plugin to `configuration.py`:

```python
PLUGINS = [
    # ...existing plugins...
    "netbox_software_discovery",
]

PLUGINS_CONFIG = {
    "netbox_software_discovery": {
        "stale_after_minutes": 60,
        "allow_auto_match": True,
        "max_payload_items": 10000,
    },
}
```

Run migrations and restart NetBox services:

```bash
cd /opt/netbox
./venv/bin/python manage.py migrate
sudo systemctl restart netbox netbox-rq
```

The plugin pages appear at `/plugins/software-discovery/`. The ingest URL is `/api/plugins/software-discovery/ingest/`.

### Create an agent API token

Create a dedicated NetBox service account and a v2 API token. Grant `add` and `change` permissions for `ReportingAgent` and `SoftwareInstallation`, plus `add` permission for `VersionEvent`. Grant `view` permissions for the inventory models if the agent account also needs to read the plugin API. The ingest endpoint enforces the write permissions. Use the token's v2 `Bearer nbt_...` form. Do not use an administrator token. NetBox 4.5 supports v2 bearer tokens; legacy `Token` is accepted by the agent for older token configurations but prefer v2.

## Install the agent on Linux

```bash
sudo useradd --system --home /opt/netbox-software-agent --shell /usr/sbin/nologin netbox-agent
sudo mkdir -p /opt/netbox-software-agent
sudo chown netbox-agent:netbox-agent /opt/netbox-software-agent
sudo -u netbox-agent python3.12 -m venv /opt/netbox-software-agent/.venv
sudo -u netbox-agent /opt/netbox-software-agent/.venv/bin/pip install 'httpx>=0.27' 'packaging>=24'
# From this repository root:
sudo -u netbox-agent /opt/netbox-software-agent/.venv/bin/pip install .
sudo install -m 0600 config/agent.env.example /etc/netbox-software-agent.env
sudoedit /etc/netbox-software-agent.env
sudo cp systemd/netbox-software-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now netbox-software-agent
```

The sample service runs as an unprivileged user. Grant only read access needed for package/service/container inventory. Docker socket access is effectively root-equivalent; consider a dedicated read-only proxy or omit container discovery rather than adding the agent to the `docker` group.

## Install the agent on Windows

Install Python 3.12, unpack this project, then in an elevated PowerShell window:

```powershell
py -3.12 -m venv C:\ProgramData\NetBoxSoftwareAgent\venv
C:\ProgramData\NetBoxSoftwareAgent\venv\Scripts\pip.exe install httpx packaging
C:\ProgramData\NetBoxSoftwareAgent\venv\Scripts\pip.exe install .
$env:NETBOX_URL = 'https://netbox.example.org'
$env:NETBOX_TOKEN = 'nbt_REPLACE_WITH_TOKEN'
$env:AGENT_ID = $env:COMPUTERNAME
C:\ProgramData\NetBoxSoftwareAgent\venv\Scripts\netbox-software-agent.exe --once
```

For continuous operation, register the executable as a Windows service using your organization's service wrapper (e.g. WinSW) and store secrets in the service manager's protected environment/configuration. Do not put tokens in command-line arguments.

## Agent configuration

| Variable | Default | Purpose |
|---|---|---|
| `NETBOX_URL` | required | NetBox base URL |
| `NETBOX_TOKEN` | required | NetBox API v2 token (`nbt_...`) |
| `AGENT_ID` | FQDN | Stable unique agent identity |
| `DISCOVERY_INTERVAL` | `900` | Seconds between reports (minimum 60) |
| `NETBOX_VERIFY_TLS` | `true` | Verify TLS certificates; keep enabled |
| `NETBOX_TIMEOUT` | `30` | HTTP timeout |
| `NETBOX_OBJECT_TYPE` | empty | `dcim.device` or `virtualization.virtualmachine` |
| `NETBOX_OBJECT_ID` | empty | Numeric NetBox object ID |
| `PROXMOX_CLUSTER/NODE/VMID` | empty | Proxmox guest metadata |
| `DISCOVER_PACKAGES` | `true` | Installed packages |
| `DISCOVER_SERVICES` | `true` | Service inventory |
| `DISCOVER_CONTAINERS` | `true` | Docker/Podman containers |
| `DISCOVER_KUBERNETES` | `true` | Kubernetes pods via kubectl |
| `COMPLETE_INVENTORY` | `false` | Mark previously seen items absent; enable only after validating every configured collector and its permissions |

## Object matching

Best practice is to set `NETBOX_OBJECT_TYPE` and `NETBOX_OBJECT_ID` on each agent. If omitted, the plugin optionally tries an exact case-insensitive hostname match, preferring a VM before a device. Hostname matching can be ambiguous in multi-tenant or multi-site environments; disable `allow_auto_match` or use explicit IDs there. The plugin never creates NetBox devices or VMs.

## API

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

## Docker

`agent.Dockerfile` and `docker-compose.agent.yml` provide a containerized agent. The container sees its own namespaces by default; it does **not** magically inventory the host. For complete host inventory, install natively or deliberately mount host resources and configure engine access with least privilege.

```bash
cp .env.example .env
# Edit .env; protect it (chmod 0600).
docker compose -f docker-compose.agent.yml up -d --build
```

## Proxmox

Install the agent inside each Linux/Windows guest. Configure `PROXMOX_CLUSTER`, `PROXMOX_NODE`, and `PROXMOX_VMID` from the guest's provisioning metadata/cloud-init. Set explicit NetBox object type/id to bind the report to the corresponding NetBox VM. This release does not call the Proxmox API or discover guest inventory from the hypervisor itself.

## Development and tests

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[agent,test]'
pytest
ruff check .
```

The unit tests cover data ingestion, version-change events and collector output. Run an integration test against a disposable NetBox 4.5.x instance before production; the test settings are not a substitute for NetBox's full Django app registry.

## Security and operational notes

- Use TLS with certificate validation; do not set `NETBOX_VERIFY_TLS=false` in production.
- Use a dedicated service account and least-privilege token. Rotate/revoke the token if an agent is compromised.
- Restrict Kubernetes RBAC to read-only `get/list` on pods and required metadata.
- Do not expose Docker/Podman sockets to untrusted workloads. Access to the Docker socket is effectively host root.
- The plugin stores inventory metadata, not secrets or environment variables.
- Package version discovery reports installed package versions; it does not determine whether a version is vulnerable or the latest available. Add an approved vulnerability/feed integration separately.
- Add reverse-proxy request size limits and network ACLs around the ingest endpoint.

## Roadmap

- Native NetBox device/VM detail tabs and object-level inventory panels.
- Proxmox API collector for VM/LXC inventory reconciliation.
- Background jobs for stale-agent alerts and scheduled version intelligence.
- CVE/OSV and vendor release feed integrations with policy-based severity.
- Collector health flags so incomplete reports never mark valid software absent.
