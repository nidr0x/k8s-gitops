resource "proxmox_storage_directory" "local" {
  id      = "local"
  path    = "/var/lib/vz"
  content = ["backup", "import", "iso", "vztmpl"]
  shared  = false

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [disable, nodes]
  }
}

resource "proxmox_storage_lvmthin" "local_lvm" {
  id           = "local-lvm"
  volume_group = "pve"
  thin_pool    = "data"
  content      = ["images", "rootdir"]

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [disable, nodes]
  }
}
