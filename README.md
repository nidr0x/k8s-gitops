<div align="center">

[![Super-Linter](https://github.com/nidr0x/k8s-gitops/actions/workflows/lint.yaml/badge.svg)](https://github.com/marketplace/actions/super-linter)
![Internet connection check](https://healthchecks.io/b/2/3cb6473d-5f04-48aa-8047-4f52d83cdcb7.svg)

# 🏡 nidr0x Homelab

Welcome to the nidr0x Homelab repository! Here you'll find [Kubernetes](https://kubernetes.io/) manifests and [Argo CD](https://argoproj.github.io/cd/) definitions for a homelab environment, all running on top of [Talos](https://talos.dev) and [Proxmox](https://www.proxmox.com/en/). This setup includes a wide range of applications, each organized into its own folder, with versioning expertly managed by [Renovate](https://www.mend.io/renovate/).

</div>

# 🧪 Purpose

The primary goal of this repository, beyond self-hosting services on my own infrastructure, is to continuously improve my skills, experiment with new technologies and methodologies, and apply this knowledge to real-world scenarios in my professional work.

## ⚙️ Application list

- [Adguard Home](https://github.com/AdguardTeam/AdGuardHome)
- [ArgoCD](https://github.com/argoproj/argo-cd)
- [CSI Driver NFS](https://github.com/kubernetes-csi/csi-driver-nfs)
- [Cilium](https://cilium.io/)
- [Cloudflared](https://github.com/cloudflare/cloudflared)
- [Cloudnative-PG](https://github.com/cloudnative-pg/cloudnative-pg)
- [External DNS](https://github.com/kubernetes-sigs/external-dns)
- [External Secrets](https://github.com/external-secrets/external-secrets)
- [FreshRSS](https://github.com/FreshRSS/FreshRSS)
- [GPhotos Sync](https://github.com/gilesknap/gphotos-sync)
- [Grafana Alloy](https://grafana.com/docs/alloy/latest/)
- [Home Assistant](https://github.com/home-assistant/docker)
- [Homebridge](https://homebridge.io/)
- [Kube Prometheus Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Loki](https://grafana.com/oss/loki/)
- [Node Problem Detector](https://github.com/kubernetes/node-problem-detector)
- [Secret Reloader](https://github.com/stakater/Reloader)
- [Teslamate](https://github.com/teslamate-org/teslamate)
- [Transmission](https://github.com/transmission/transmission)
- [Uptime Kuma](https://github.com/louislam/uptime-kuma)
- [Unbound](https://www.nlnetlabs.nl/projects/unbound/about/)
- [Vaultwarden](https://github.com/dani-garcia/vaultwarden)
- [cert-manager](https://github.com/cert-manager/cert-manager)
- [kubelet serving cert approver](https://github.com/alex1989hu/kubelet-serving-cert-approver)

## 🛠️ Changelog

Check the [commit history](https://github.com/nidr0x/k8s-gitops/commits/master)

## 🔗 External cloud dependencies

While most of my infrastructure and workloads are self-hosted I do rely upon the cloud for certain key parts of my setup. This saves me from having to worry about two things. Dealing with chicken/egg scenarios and services I critically need whether my cluster is online or not.

| Service                                    | Use                                                                                               | Cost                 |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------- | -------------------- |
| [Cloudflare](https://www.cloudflare.com/)  | Domain & R2 (Database backups) & Cloudflare tunnels (exposing applications) & Oauth ( Zero Trust) | ~$10/yr              |
| [GitHub](https://www.github.com/)          | Repository & CI/CD                                                                                | Free                 |
| [Brevo](https://www.brevo.com/)            | SMTP email platform                                                                               | Free (up to 300/day) |
| [ZeroSSL](https://www.zerossl.com/)        | Issuing SSL Certificates via Cert Manager                                                         | Free                 |
| [Doppler](https://www.doppler.com/)        | Secrets management platform                                                                       | Free                 |
| [healthchecks.io](https://healthchecks.io) | Monitoring internet connectivity                                                                  | Free                 |

## 📁 Repository structure

The repository is organized into folders by application. Each folder contains the necessary manifest files to deploy the application on a Kubernetes cluster. The `argocd` folder contains files for setting up and managing ArgoCD.

## 🌐 Public Services

As part of my commitment to open-source communities, I offer these public services:

**DNS-over-HTTPS (DoH)**
🔗 `https://dns.nidr0x.win/dns-query`

It is powered by [AdGuard Home](https://github.com/AdguardTeam/AdGuardHome) + [Cloudflare](https://www.cloudflare.com). The configuration that uses is available [here](https://github.com/nidr0x/k8s-gitops/blob/master/kubernetes/main/apps/adguardhome/config/AdGuardHome.yaml)
