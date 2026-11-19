import {
  to = proxmox_network_linux_bridge.vmbr0
  id = "everest:vmbr0"
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
  to = proxmox_node_config.everest
  id = "everest"
}

import {
  to = proxmox_cluster_options.cluster
  id = "datacenter"
}

import {
  to = proxmox_virtual_environment_vm.controlplane_01
  id = "everest/100"
}

import {
  to = proxmox_virtual_environment_vm.worker_01
  id = "everest/101"
}

import {
  to = proxmox_virtual_environment_vm.controlplane_02
  id = "everest/103"
}

import {
  to = proxmox_virtual_environment_vm.worker_03
  id = "k2/104"
}

import {
  to = proxmox_virtual_environment_vm.worker_02
  id = "k2/105"
}

import {
  to = proxmox_virtual_environment_vm.controlplane_03
  id = "k2/106"
}

import {
  to = proxmox_virtual_environment_vm.opensre
  id = "everest/107"
}
