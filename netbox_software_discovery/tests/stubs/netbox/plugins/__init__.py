from django.apps import AppConfig


class PluginConfig(AppConfig):
    """NetBox's PluginConfig is an AppConfig with extra metadata attributes."""

    base_url = None
    min_version = None
    max_version = None
    required_settings: list = []
    default_settings: dict = {}


class PluginMenuItem:
    def __init__(self, link, link_text, permissions=None, buttons=None):
        self.link, self.link_text, self.permissions = link, link_text, permissions or []


class PluginMenu:
    def __init__(self, label, groups, icon_class=None):
        self.label, self.groups, self.icon_class = label, groups, icon_class
