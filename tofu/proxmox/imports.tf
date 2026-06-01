import {
  to = proxmox_network_linux_bridge.vmbr0
  id = "annapurna:vmbr0"
}

import {
  to = proxmox_storage_directory.local
  id = "local"
}

import {
  to = proxmox_storage_lvmthin.local_lvm
  id = "local-lvm"
}

import {
  to = proxmox_node_config.annapurna
  id = "annapurna"
}

import {
  to = proxmox_cluster_options.cluster
  id = "datacenter"
}

import {
  to = proxmox_virtual_environment_vm.controlplane_01
  id = "annapurna/100"
}

import {
  to = proxmox_virtual_environment_vm.worker_01
  id = "annapurna/101"
}

import {
  to = proxmox_virtual_environment_vm.debian_12_template
  id = "annapurna/102"
}

import {
  to = proxmox_virtual_environment_vm.controlplane_02
  id = "annapurna/103"
}

import {
  to = proxmox_virtual_environment_vm.worker_03
  id = "annapurna/104"
}

import {
  to = proxmox_virtual_environment_vm.worker_02
  id = "annapurna/105"
}

import {
  to = proxmox_virtual_environment_vm.controlplane_03
  id = "annapurna/106"
}

import {
  to = proxmox_virtual_environment_vm.opensre
  id = "annapurna/107"
}
