# Install the agent on Linux

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
