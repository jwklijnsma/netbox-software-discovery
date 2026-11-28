# Agent configuration

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
