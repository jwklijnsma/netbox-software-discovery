# Object matching

Best practice is to set `NETBOX_OBJECT_TYPE` and `NETBOX_OBJECT_ID` on each agent. If omitted, the plugin optionally tries an exact case-insensitive hostname match, preferring a VM before a device. Hostname matching can be ambiguous in multi-tenant or multi-site environments; disable `allow_auto_match` or use explicit IDs there. The plugin never creates NetBox devices or VMs.
