from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    label="Software Discovery",
    icon_class="mdi mdi-package-variant-closed",
    groups=(("Inventory", (
        PluginMenuItem(link="plugins:netbox_software_discovery:software_list", link_text="Software inventory"),
        PluginMenuItem(link="plugins:netbox_software_discovery:agent_list", link_text="Reporting agents"),
    )),),
)
