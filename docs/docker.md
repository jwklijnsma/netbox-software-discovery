# Docker

`agent.Dockerfile` and `docker-compose.agent.yml` provide a containerized agent. The container sees its own namespaces by default; it does **not** magically inventory the host. For complete host inventory, install natively or deliberately mount host resources and configure engine access with least privilege.

```bash
cp .env.example .env
# Edit .env; protect it (chmod 0600).
docker compose -f docker-compose.agent.yml up -d --build
```
