# Install the NetBox plugin

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

## Create an agent API token

Create a dedicated NetBox service account and a v2 API token. Grant `add` and `change` permissions for `ReportingAgent` and `SoftwareInstallation`, plus `add` permission for `VersionEvent`. Grant `view` permissions for the inventory models if the agent account also needs to read the plugin API. The ingest endpoint enforces the write permissions. Use the token's v2 `Bearer nbt_...` form. Do not use an administrator token. NetBox 4.5 supports v2 bearer tokens; legacy `Token` is accepted by the agent for older token configurations but prefer v2.
