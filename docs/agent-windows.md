# Install the agent on Windows

Install Python 3.12, unpack this project, then in an elevated PowerShell window:

```powershell
py -3.12 -m venv C:\ProgramData\NetBoxSoftwareAgent\venv
C:\ProgramData\NetBoxSoftwareAgent\venv\Scripts\pip.exe install httpx packaging
C:\ProgramData\NetBoxSoftwareAgent\venv\Scripts\pip.exe install .
$env:NETBOX_URL = 'https://netbox.example.org'
$env:NETBOX_TOKEN = 'nbt_REPLACE_WITH_TOKEN'
$env:AGENT_ID = $env:COMPUTERNAME
C:\ProgramData\NetBoxSoftwareAgent\venv\Scripts\netbox-software-agent.exe --once
```

For continuous operation, register the executable as a Windows service using your organization's service wrapper (e.g. WinSW) and store secrets in the service manager's protected environment/configuration. Do not put tokens in command-line arguments.
