SECRET_KEY="test-secret"
INSTALLED_APPS=["django.contrib.auth","django.contrib.contenttypes","rest_framework","netbox_software_discovery"]
DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":":memory:"}}
ROOT_URLCONF="netbox_software_discovery.tests.urls"
PLUGINS_CONFIG={"netbox_software_discovery":{"allow_auto_match":False,"max_payload_items":1000}}
USE_TZ=True
INSTALLED_APPS += ["django.contrib.sessions"]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
LOGIN_URL = "/login/"
