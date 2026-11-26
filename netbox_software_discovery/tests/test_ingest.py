import pytest
from netbox_software_discovery.services import ingest_report
from netbox_software_discovery.models import ReportingAgent, SoftwareInstallation, VersionEvent

@pytest.mark.django_db
def test_ingest_and_version_change():
    payload={"agent_id":"agent-1","hostname":"db01","os_name":"Ubuntu","os_version":"24.04","software":[{"name":"postgresql","version":"16","category":"package","source":"dpkg"}],"complete_inventory":True}
    agent,count,obj=ingest_report(payload)
    assert count==1 and obj is None
    payload["software"][0]["version"]="17"
    ingest_report(payload)
    item=SoftwareInstallation.objects.get(agent=agent,name="postgresql")
    assert item.version=="17"
    assert VersionEvent.objects.filter(installation=item,previous_version="16",new_version="17").exists()

@pytest.mark.django_db
def test_missing_required_fields_rejected():
    with pytest.raises(ValueError): ingest_report({"hostname":"missing-agent","software":[]})
