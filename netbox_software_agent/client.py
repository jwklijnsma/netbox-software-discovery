import httpx
from . import __version__

def send_report(config, payload):
    if not config.netbox_url or not config.netbox_token:
        raise RuntimeError("NETBOX_URL and NETBOX_TOKEN must be configured")
    url=f"{config.netbox_url}/api/plugins/software-discovery/ingest/"
    headers={"Authorization": config.netbox_token if config.netbox_token.startswith("Bearer ") or config.netbox_token.startswith("Token ") else f"Token {config.netbox_token}", "User-Agent":f"netbox-software-agent/{__version__}"}
    with httpx.Client(timeout=config.timeout, verify=config.verify_tls) as client:
        response=client.post(url,json=payload,headers=headers)
        response.raise_for_status()
        return response.json()
