# Compatibility

| Plugin release | NetBox minimum | NetBox maximum | Python |
|---|---:|---:|---|
| 0.1.0 | 4.5.0 | 4.7.x | 3.12+ |

Checked on NetBox 4.7.6: `manage.py check` passes and `migrate --plan` creates the plugin tables. NetBox 4.5.x remains the original target.

NetBox without `API_TOKEN_PEPPERS` cannot use v2 tokens; agents then use a classic token (`NETBOX_TOKEN` without the `nbt_` prefix is sent as `Token ...`). Run the integration test matrix against the exact
NetBox patch release used in production before deploying.
