from django.urls import path
from . import views

app_name = "netbox_software_discovery"
urlpatterns = [
    path("", views.SoftwareListView.as_view(), name="software_list"),
    path("software/<int:pk>/", views.SoftwareDetailView.as_view(), name="software_detail"),
    path("agents/", views.AgentListView.as_view(), name="agent_list"),
]
