terraform {
  backend "kubernetes" {
    secret_suffix = "state"
    namespace     = "kube-system"
    config_path   = "~/.kube/config"
  }
}
