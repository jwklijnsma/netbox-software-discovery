from netbox_software_agent import collectors

def test_os_info_has_required_fields():
    info=collectors.os_info()
    assert info["os_name"] and info["os_version"] and info["architecture"]

def test_container_inventory_is_list(monkeypatch):
    monkeypatch.setattr(collectors.shutil,"which",lambda _: None)
    assert collectors.container_inventory()==[]

def test_collect_report_shape(monkeypatch):
    class C: include_packages=False; include_services=False; include_containers=False; include_kubernetes=False; agent_id="test"; proxmox_cluster=""; proxmox_node=""; proxmox_vmid=""; netbox_object_type=""; netbox_object_id=""; complete_inventory=False
    report=collectors.collect(C())
    assert report["agent_id"]=="test" and isinstance(report["software"],list)
