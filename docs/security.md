# Security and operational notes

- Use TLS with certificate validation; do not set `NETBOX_VERIFY_TLS=false` in production.
- Use a dedicated service account and least-privilege token. Rotate/revoke the token if an agent is compromised.
- Restrict Kubernetes RBAC to read-only `get/list` on pods and required metadata.
- Do not expose Docker/Podman sockets to untrusted workloads. Access to the Docker socket is effectively host root.
- The plugin stores inventory metadata, not secrets or environment variables.
- Package version discovery reports installed package versions; it does not determine whether a version is vulnerable or the latest available. Add an approved vulnerability/feed integration separately.
- Add reverse-proxy request size limits and network ACLs around the ingest endpoint.
