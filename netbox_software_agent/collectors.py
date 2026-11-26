"""Cross-platform inventory collectors. Collectors are best-effort and never execute shell strings."""
import json, os, platform, re, shutil, socket, subprocess, sys
from pathlib import Path

def run(args, timeout=15):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return p.stdout.strip() if p.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""

def os_info():
    info = {"os_name": platform.system(), "os_version": platform.release(), "architecture": platform.machine()}
    if sys.platform.startswith("linux"):
        try:
            data = {}
            for line in Path("/etc/os-release").read_text().splitlines():
                if "=" in line:
                    k,v=line.split("=",1); data[k]=v.strip().strip('"')
            info.update(os_name=data.get("PRETTY_NAME", data.get("NAME", "Linux")), os_version=data.get("VERSION_ID", platform.release()))
        except OSError: pass
    elif sys.platform == "win32":
        out=run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).Caption + '|' + (Get-CimInstance Win32_OperatingSystem).Version"])
        if "|" in out: info["os_name"],info["os_version"]=out.split("|",1)
    return info

def network_info():
    ips=[]
    try:
        for result in socket.getaddrinfo(socket.gethostname(), None):
            ip=result[4][0]
            if ":" not in ip and not ip.startswith("127.") and ip not in ips: ips.append(ip)
    except OSError: pass
    return ips[:32]

def package_inventory():
    items=[]
    if sys.platform.startswith("linux"):
        if shutil.which("dpkg-query"):
            out=run(["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\t${Architecture}\n"], timeout=60)
            for line in out.splitlines():
                p=line.split("\t")
                if len(p)>=2: items.append({"name":p[0],"version":p[1],"architecture":p[2] if len(p)>2 else "","category":"package","source":"dpkg","status":"installed"})
        elif shutil.which("rpm"):
            out=run(["rpm", "-qa", "--qf", "%{NAME}\t%{VERSION}-%{RELEASE}\t%{ARCH}\n"], timeout=60)
            for line in out.splitlines():
                p=line.split("\t")
                if len(p)>=2: items.append({"name":p[0],"version":p[1],"architecture":p[2] if len(p)>2 else "","category":"package","source":"rpm","status":"installed"})
        elif shutil.which("apk"):
            for line in run(["apk", "info", "-v"], timeout=60).splitlines():
                if "-" in line:
                    name,version=line.rsplit("-",1); items.append({"name":name,"version":version,"category":"package","source":"apk","status":"installed"})
    elif sys.platform == "win32":
        ps=r"$paths=@('HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'); Get-ItemProperty $paths -ErrorAction SilentlyContinue | Where-Object DisplayName | Select-Object DisplayName,DisplayVersion,Publisher | ConvertTo-Json -Compress"
        out=run(["powershell", "-NoProfile", "-Command", ps], timeout=60)
        try:
            data=json.loads(out) if out else []
            if isinstance(data,dict): data=[data]
            for x in data: items.append({"name":x.get("DisplayName",""),"version":x.get("DisplayVersion","") or "","vendor":x.get("Publisher","") or "","category":"package","source":"windows-registry","status":"installed"})
        except json.JSONDecodeError: pass
    return items

def service_inventory():
    items=[]
    if sys.platform.startswith("linux") and shutil.which("systemctl"):
        out=run(["systemctl", "list-units", "--type=service", "--all", "--no-legend", "--no-pager"], timeout=30)
        for line in out.splitlines():
            p=line.split()
            if len(p)>=4: items.append({"name":p[0].removesuffix(".service"),"version":"","category":"service","source":"systemd","status":"running" if p[2]=="active" else "stopped","metadata":{"load":p[1],"active_state":p[2],"sub_state":p[3]}})
    elif sys.platform == "win32":
        out=run(["powershell","-NoProfile","-Command","Get-Service | Select-Object Name,Status,DisplayName | ConvertTo-Json -Compress"],timeout=30)
        try:
            data=json.loads(out) if out else []
            if isinstance(data,dict): data=[data]
            for x in data: items.append({"name":x.get("Name",""),"version":"","category":"service","source":"windows-service","status":"running" if x.get("Status")=="Running" else "stopped","metadata":{"display_name":x.get("DisplayName","")}})
        except json.JSONDecodeError: pass
    return items

def container_inventory():
    items=[]
    for engine in ("docker","podman"):
        if not shutil.which(engine): continue
        out=run([engine,"ps","-a","--no-trunc","--format","{{json .}}"],timeout=30)
        for line in out.splitlines():
            try: x=json.loads(line)
            except json.JSONDecodeError: continue
            image=x.get("Image",""); name=x.get("Names","") or x.get("Name","")
            items.append({"name":name or image,"version":image.rsplit(":",1)[-1] if ":" in image else "latest","category":"container","source":engine,"status":"running" if x.get("State","").lower()=="running" else "stopped","image":image,"metadata":{"container_id":x.get("ID",""),"state":x.get("State",""),"status_text":x.get("Status","")}})
    return items

def kubernetes_inventory():
    items=[]
    if not shutil.which("kubectl"): return items
    out=run(["kubectl","get","pods","--all-namespaces","-o","json"],timeout=45)
    try: data=json.loads(out) if out else {}
    except json.JSONDecodeError: return items
    for pod in data.get("items",[]):
        meta=pod.get("metadata",{}); status=pod.get("status",{}); ns=meta.get("namespace","")
        for container in status.get("containerStatuses",[]):
            image=container.get("image",""); name=container.get("name","")
            items.append({"name":f"{ns}/{meta.get('name','')}/{name}","version":image.rsplit(":",1)[-1] if ":" in image else "latest","category":"kubernetes","source":"kubectl","status":"running" if container.get("state",{}).get("running") else "stopped","image":image,"metadata":{"namespace":ns,"pod":meta.get("name",""),"container":name,"ready":container.get("ready",False)}})
    return items

def collect(config):
    info=os_info()
    items=[{"name":info["os_name"],"version":info["os_version"],"category":"os","source":"system","status":"running","architecture":info["architecture"]}]
    if config.include_packages: items.extend(package_inventory())
    if config.include_services: items.extend(service_inventory())
    if config.include_containers: items.extend(container_inventory())
    if config.include_kubernetes: items.extend(kubernetes_inventory())
    # Include hypervisor guest identity as metadata, not as guessed NetBox linkage.
    pve={"cluster":config.proxmox_cluster,"node":config.proxmox_node,"vmid":config.proxmox_vmid}
    return {"agent_id":config.agent_id or socket.getfqdn(),"hostname":socket.gethostname(),"fqdn":socket.getfqdn(),**info,"ip_addresses":network_info(),"agent_version":"0.1.0",
            "proxmox_cluster":pve["cluster"],"proxmox_node":pve["node"],"proxmox_vmid":pve["vmid"],
            "netbox_object_type":config.netbox_object_type or None,"netbox_object_id":int(config.netbox_object_id) if config.netbox_object_id else None,
            "complete_inventory":config.complete_inventory,"software":items}
