resource "proxmox_virtual_environment_vm" "controlplane_01" {
  name      = "controlplane-01"
  node_name = "annapurna"
  vm_id     = 100
  bios      = "ovmf"
  machine   = "q35"
  on_boot   = true
  started   = true
  tags      = ["controlplane"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 2
    sockets = 1
    type    = "host"
  }

  memory {
    dedicated = 8000
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = false
    mac_address = "BC:24:11:9C:06:43"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      efi_disk,
      keyboard_layout,
      smbios,
      startup,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "worker_01" {
  name      = "worker-01"
  node_name = "annapurna"
  vm_id     = 101
  bios      = "ovmf"
  machine   = "q35"
  on_boot   = true
  started   = true
  tags      = ["worker"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 4
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 15000
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = true
    mac_address = "BC:24:11:85:FB:FC"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      efi_disk,
      keyboard_layout,
      smbios,
      startup,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "debian_12_template" {
  name      = "debian-12-template"
  node_name = "annapurna"
  vm_id     = 102
  on_boot   = false
  started   = false
  tags      = ["template", "opensre"]
  template  = true

  agent {
    enabled = true
  }

  cpu {
    cores   = 1
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 2048
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = false
    mac_address = "BC:24:11:22:1F:F4"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      initialization,
      keyboard_layout,
      serial_device,
      smbios,
      vga,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "controlplane_02" {
  name      = "controlplane-02"
  node_name = "annapurna"
  vm_id     = 103
  bios      = "ovmf"
  machine   = "q35"
  on_boot   = true
  started   = true
  tags      = ["controlplane"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 2
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 8000
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = true
    mac_address = "BC:24:11:75:DD:27"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      efi_disk,
      keyboard_layout,
      smbios,
      startup,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "worker_03" {
  name      = "worker-03"
  node_name = "annapurna"
  vm_id     = 104
  bios      = "ovmf"
  machine   = "q35"
  on_boot   = true
  started   = true
  tags      = ["worker"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 4
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 16000
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = true
    mac_address = "BC:24:11:B0:90:FC"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      efi_disk,
      keyboard_layout,
      smbios,
      startup,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "worker_02" {
  name      = "worker-02"
  node_name = "annapurna"
  vm_id     = 105
  bios      = "ovmf"
  machine   = "q35"
  on_boot   = true
  started   = true
  tags      = ["worker"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 4
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 16000
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = true
    mac_address = "BC:24:11:CA:61:A3"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      efi_disk,
      keyboard_layout,
      smbios,
      startup,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "controlplane_03" {
  name      = "controlplane-03"
  node_name = "annapurna"
  vm_id     = 106
  bios      = "ovmf"
  machine   = "q35"
  on_boot   = true
  started   = true
  tags      = ["controlplane"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 2
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 8000
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = true
    mac_address = "BC:24:11:FA:05:75"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      efi_disk,
      keyboard_layout,
      smbios,
      startup,
    ]
  }
}

resource "proxmox_virtual_environment_vm" "opensre" {
  name      = "opensre"
  node_name = "annapurna"
  vm_id     = 107
  on_boot   = true
  started   = true
  tags      = ["opensre"]

  agent {
    enabled = true
  }

  cpu {
    cores   = 1
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 2048
  }

  network_device {
    bridge      = "vmbr0"
    firewall    = false
    mac_address = "BC:24:11:51:E7:E0"
    model       = "virtio"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      agent,
      boot_order,
      cdrom,
      disk,
      initialization,
      keyboard_layout,
      serial_device,
      smbios,
      vga,
    ]
  }
}
