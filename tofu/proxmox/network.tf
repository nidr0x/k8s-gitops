resource "proxmox_network_linux_bridge" "vmbr0" {
  node_name = "annapurna"
  name      = "vmbr0"

  address   = "192.168.1.11/24"
  gateway   = "192.168.1.1"
  autostart = true
  ports     = ["enp2s0"]

  lifecycle {
    prevent_destroy = true
  }
}
