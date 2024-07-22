resource "talos_machine_secrets" "this" {}

data "talos_machine_configuration" "this" {
  cluster_name     = "everest"
  machine_type     = "controlplane"
  cluster_endpoint = "https://192.168.1.11:6443"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
}

data "talos_client_configuration" "this" {
  cluster_name         = "everest"
  client_configuration = talos_machine_secrets.this.client_configuration
  nodes                = ["192.168.1.11"]
}

data "talos_cluster_kubeconfig" "this" {
  depends_on = [
    talos_machine_bootstrap.this
  ]
  client_configuration = talos_machine_secrets.this.client_configuration
  node                 = "192.168.1.11"
}

resource "talos_machine_configuration_apply" "this" {
  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.this.machine_configuration
  node                        = "192.168.1.11"
  config_patches = [
    file("${path.module}/talos-patch.yaml")
  ]
}

resource "talos_machine_bootstrap" "this" {
  depends_on = [
    talos_machine_configuration_apply.this
  ]
  node                 = "192.168.1.11"
  client_configuration = talos_machine_secrets.this.client_configuration
}
