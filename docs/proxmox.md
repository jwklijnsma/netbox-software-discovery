# Proxmox

Install the agent inside each Linux/Windows guest. Configure `PROXMOX_CLUSTER`, `PROXMOX_NODE`, and `PROXMOX_VMID` from the guest's provisioning metadata/cloud-init. Set explicit NetBox object type/id to bind the report to the corresponding NetBox VM. This release does not call the Proxmox API or discover guest inventory from the hypervisor itself.
