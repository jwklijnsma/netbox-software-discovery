# NetBox Software Discovery

**Agent-based software inventory for NetBox 4.5.x.** A small Python agent inventories the
operating system, installed packages, services, Docker/Podman containers and (with
`kubectl`) Kubernetes pods, and reports them to a NetBox plugin over HTTPS.

<div class="grid cards" markdown>

-   :material-puzzle: **[NetBox plugin](plugin.md)**

    Install the plugin and its API token.

-   :simple-linux: **[Agent on Linux](agent-linux.md)**

    dpkg, RPM or APK packages, systemd services, containers.

-   :material-microsoft-windows: **[Agent on Windows](agent-windows.md)**

    Installed software from the uninstall registry, Windows services.

-   :simple-proxmox: **[Proxmox](proxmox.md)**

    Record VMID, node and cluster for guest agents.

</div>

## Features

| Feature | What you get |
|---|---|
| **Plugin models** | Reporting agents, software installations and version-change events |
| **Ingest API** | Authenticated `POST /api/plugins/software-discovery/ingest/` |
| **Read API and UI** | REST endpoints and inventory pages under `/plugins/software-discovery/` |
| **Discovery** | Linux packages, Windows software, services, Docker/Podman, Kubernetes pods |
| **Object binding** | Explicit `NETBOX_OBJECT_TYPE` + `NETBOX_OBJECT_ID`, or conservative hostname matching |
| **History** | Version changes and stale marking on complete inventories |

!!! note "Proxmox scope"
    Install the agent inside each guest VM or LXC. This release doesn't query the Proxmox API
    or create NetBox VMs; the optional Proxmox variables only record where a guest runs.
