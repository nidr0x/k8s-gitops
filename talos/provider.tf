terraform {
  required_version = ">= 1.9"
  required_providers {
    talos = {
      source  = "siderolabs/talos"
      version = "0.6.0"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4"
    }
  }
}

provider "talos" {}
