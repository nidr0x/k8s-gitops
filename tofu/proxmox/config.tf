resource "proxmox_node_config" "annapurna" {
  node_name = "annapurna"

  lifecycle {
    prevent_destroy = true
  }
}

resource "proxmox_cluster_options" "cluster" {
  keyboard   = "es"
  mac_prefix = "BC:24:11"

  lifecycle {
    prevent_destroy = true
  }
}
