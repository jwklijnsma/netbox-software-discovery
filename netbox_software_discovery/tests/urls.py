from django.urls import include, path
urlpatterns=[path("plugins/software-discovery/",include("netbox_software_discovery.urls"))]
