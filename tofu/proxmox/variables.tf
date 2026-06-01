variable "proxmox_api_endpoint" {
  description = "Proxmox API endpoint, for example https://pve.example.com:8006/."
  type        = string
  default     = null
  nullable    = true
}

variable "proxmox_api_token" {
  description = "Proxmox API token in user@realm!tokenid=secret format."
  type        = string
  default     = null
  nullable    = true
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Whether to skip TLS certificate verification for the Proxmox API."
  type        = bool
  default     = false
}

variable "proxmox_ssh_username" {
  description = "SSH username used by the provider for VM and file operations."
  type        = string
  default     = null
  nullable    = true
}

variable "proxmox_ssh_private_key" {
  description = "PEM-encoded SSH private key used by the provider when agent auth is not available."
  type        = string
  default     = null
  nullable    = true
  sensitive   = true
}

variable "proxmox_ssh_agent" {
  description = "Whether to use the local SSH agent for Proxmox node access."
  type        = bool
  default     = true
}

variable "annapurna_ssh_address" {
  description = "SSH-reachable address for the annapurna Proxmox node."
  type        = string
  default     = null
  nullable    = true
}
