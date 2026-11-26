from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

class ReportingAgent(models.Model):
    """Last-seen identity and health of an installed discovery agent."""
    agent_id = models.CharField(max_length=128, unique=True)
    hostname = models.CharField(max_length=255, db_index=True)
    fqdn = models.CharField(max_length=255, blank=True)
    os_name = models.CharField(max_length=128, blank=True)
    os_version = models.CharField(max_length=128, blank=True)
    architecture = models.CharField(max_length=64, blank=True)
    agent_version = models.CharField(max_length=32, blank=True)
    ip_addresses = models.JSONField(default=list, blank=True)
    proxmox_cluster = models.CharField(max_length=128, blank=True)
    proxmox_node = models.CharField(max_length=128, blank=True)
    proxmox_vmid = models.CharField(max_length=32, blank=True)
    netbox_object_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True, related_name="software_discovery_agents")
    netbox_object_id = models.PositiveBigIntegerField(null=True, blank=True)
    netbox_object = GenericForeignKey("netbox_object_type", "netbox_object_id")
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)
    last_error = models.TextField(blank=True)
    class Meta:
        ordering = ["hostname"]
    def __str__(self):
        return f"{self.hostname} ({self.agent_id})"

class SoftwareInstallation(models.Model):
    """A software item reported by an agent, linked to a NetBox device or VM."""
    CATEGORY_CHOICES = [(v, v.title()) for v in ("os", "package", "service", "container", "kubernetes", "runtime", "other")]
    STATUS_CHOICES = [("running", "Running"), ("installed", "Installed"), ("stopped", "Stopped"), ("unknown", "Unknown")]
    agent = models.ForeignKey(ReportingAgent, on_delete=models.CASCADE, related_name="installations")
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="software_installations", null=True, blank=True)
    object_id = models.PositiveBigIntegerField(null=True, blank=True)
    netbox_object = GenericForeignKey("object_type", "object_id")
    name = models.CharField(max_length=255, db_index=True)
    version = models.CharField(max_length=255, blank=True, db_index=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="package", db_index=True)
    source = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="unknown")
    vendor = models.CharField(max_length=255, blank=True)
    architecture = models.CharField(max_length=64, blank=True)
    image = models.CharField(max_length=512, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)
    is_present = models.BooleanField(default=True, db_index=True)
    class Meta:
        ordering = ["name", "version"]
        constraints = [models.UniqueConstraint(fields=["agent", "name", "category", "source"], name="nb_sd_unique_installation")]
        indexes = [models.Index(fields=["category", "name"], name="nb_sd_category_name"), models.Index(fields=["agent", "is_present"], name="nb_sd_agent_present")]
    def __str__(self):
        return f"{self.name} {self.version}".strip()
    def get_absolute_url(self):
        return reverse("plugins:netbox_software_discovery:software_detail", args=[self.pk])

class VersionEvent(models.Model):
    installation = models.ForeignKey(SoftwareInstallation, on_delete=models.CASCADE, related_name="events")
    previous_version = models.CharField(max_length=255, blank=True)
    new_version = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=32, default="version_changed")
    observed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        ordering = ["-observed_at"]
