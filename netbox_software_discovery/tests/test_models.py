import pytest
from django.contrib.contenttypes.models import ContentType
from netbox_software_discovery.models import ReportingAgent, SoftwareInstallation, VersionEvent

@pytest.mark.django_db
def test_agent_and_installation_create():
    agent=ReportingAgent.objects.create(agent_id="test-1",hostname="vm01")
    item=SoftwareInstallation.objects.create(agent=agent,name="nginx",version="1.26",category="package")
    assert str(item)=="nginx 1.26"
    assert item.is_present is True

@pytest.mark.django_db
def test_version_event_relationship():
    agent=ReportingAgent.objects.create(agent_id="test-2",hostname="vm02")
    item=SoftwareInstallation.objects.create(agent=agent,name="postgresql",version="16")
    event=VersionEvent.objects.create(installation=item,previous_version="15",new_version="16")
    assert item.events.first()==event
