provider "proxmox" {
  endpoint  = var.proxmox_api_endpoint
  api_token = var.proxmox_api_token
  insecure  = var.proxmox_insecure

  ssh {
    agent       = var.proxmox_ssh_agent
    username    = var.proxmox_ssh_username
    private_key = var.proxmox_ssh_private_key

    dynamic "node" {
      for_each = var.proxmox_ssh_address == null ? [] : [var.proxmox_ssh_address]

      content {
        name    = "everest"
        address = node.value
      }
    }
  }
}
