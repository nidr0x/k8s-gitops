resource "talos_machine_secrets" "this" {}

data "talos_machine_configuration" "controlplane" {
  cluster_name     = "everest"
  machine_type     = "controlplane"
  cluster_endpoint = "https://192.168.1.90:6443"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

data "talos_machine_configuration" "worker" {
  cluster_name     = "everest"
  machine_type     = "worker"
  cluster_endpoint = "https://192.168.1.90:6443"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

data "talos_client_configuration" "this" {
  cluster_name         = "everest"
  client_configuration = talos_machine_secrets.this.client_configuration
  nodes                = ["192.168.1.90"]
}

data "talos_cluster_kubeconfig" "this" {
  depends_on = [
    talos_machine_bootstrap.this
  ]
  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = "192.168.1.90"
}

resource "talos_machine_configuration_apply" "controlplane" {
  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane.machine_configuration
  node                        = "192.168.1.90"
  config_patches = [
    file("${path.module}/talos-patch-controlplane.yaml")
  ]
}

resource "talos_machine_configuration_apply" "worker" {
  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.worker.machine_configuration
  node                        = "192.168.1.91"
  config_patches = [
    file("${path.module}/talos-patch-worker.yaml")
  ]
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [
    talos_machine_configuration_apply.controlplane
  ]
  node                 = "192.168.1.90"
  client_configuration = talos_machine_secrets.this.client_configuration
}
