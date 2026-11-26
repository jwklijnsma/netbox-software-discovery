from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from .models import ReportingAgent, SoftwareInstallation

class SoftwareListView(LoginRequiredMixin, ListView):
    model = SoftwareInstallation
    template_name = "netbox_software_discovery/software_list.html"
    context_object_name = "software_list"
    paginate_by = 100
    def get_queryset(self):
        qs = SoftwareInstallation.objects.select_related("agent").filter(is_present=True)
        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        if q: qs = qs.filter(name__icontains=q) | qs.filter(version__icontains=q)
        if category: qs = qs.filter(category=category)
        return qs

class SoftwareDetailView(LoginRequiredMixin, DetailView):
    model = SoftwareInstallation
    template_name = "netbox_software_discovery/software_detail.html"

class AgentListView(LoginRequiredMixin, ListView):
    model = ReportingAgent
    template_name = "netbox_software_discovery/agent_list.html"
    context_object_name = "agents"
