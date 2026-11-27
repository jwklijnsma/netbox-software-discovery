"""How NetBox loads the plugin: these broke startup on a real NetBox before."""

import importlib

import pytest


def test_package_exports_config():
    # NetBox imports the package and reads `config`; without it NetBox does not start.
    import netbox_software_discovery

    cfg = netbox_software_discovery.config
    assert cfg.name == "netbox_software_discovery"
    assert cfg.base_url == "software-discovery"


def test_supports_current_netbox():
    from netbox_software_discovery import config

    major_minor = tuple(int(x) for x in config.max_version.split(".")[:2])
    assert major_minor >= (4, 7), "NetBox refuses to start a plugin outside min/max_version"


@pytest.mark.parametrize("module", [
    "netbox_software_discovery.api.urls",
    "netbox_software_discovery.api.serializers",
    "netbox_software_discovery.api.views",
    "netbox_software_discovery.urls",
    "netbox_software_discovery.views",
    "netbox_software_discovery.navigation",
])
def test_modules_netbox_imports_load(module):
    importlib.import_module(module)


@pytest.mark.django_db
@pytest.mark.parametrize("path", [
    "/plugins/software-discovery/",
    "/plugins/software-discovery/agents/",
    "/plugins/software-discovery/software/1/",
])
def test_ui_pages_need_login(client, path):
    r = client.get(path)
    assert r.status_code == 302 and r.url.startswith("/login/")
