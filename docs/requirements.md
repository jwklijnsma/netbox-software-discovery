# Requirements

- NetBox 4.5.x and Python 3.12+ on the NetBox application environment.
- Python 3.12+ on Linux/Windows agent hosts.
- Agent outbound connectivity to NetBox HTTPS.
- For Kubernetes discovery, `kubectl` installed and configured with read-only permissions to list pods across the namespaces you want inventoried.
- For Docker/Podman discovery, the agent user needs permission to query the respective engine socket.
