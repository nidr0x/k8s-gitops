<div align="center">

[![Super-Linter](https://github.com/nidr0x/k8s-gitops/actions/workflows/lint.yaml/badge.svg)](https://github.com/marketplace/actions/super-linter)

# 🏡 nidr0x Homelab

Welcome to the nidr0x Homelab repository! Here you'll find [Kubernetes](https://kubernetes.io/) manifests and [Argo CD](https://argoproj.github.io/cd/) definitions for a homelab environment, all running on top of [Talos](https://talos.dev) and [Proxmox](https://www.proxmox.com/en/). This setup includes a wide range of applications, each organized into its own folder, with versioning expertly managed by [Renovate](https://www.mend.io/renovate/).

</div>

## ⚙️ Application list

- [Adguard Home](https://github.com/AdguardTeam/AdGuardHome)
- [ArgoCD](https://github.com/argoproj/argo-cd)
- [CSI Driver NFS](https://github.com/kubernetes-csi/csi-driver-nfs)
- [Cilium](https://cilium.io/)
- [Cloudflare DDNS Updater](https://github.com/nidr0x/cloudflare-ddns-updater)
- [External DNS](https://github.com/kubernetes-sigs/external-dns)
- [External Secrets](https://github.com/external-secrets/external-secrets)
- [FreshRSS](https://github.com/FreshRSS/FreshRSS)
- [GPhotos Sync](https://github.com/gilesknap/gphotos-sync)
- [Home Assistant](https://github.com/home-assistant/docker)
- [Kube Prometheus Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Loki](https://grafana.com/oss/loki/)
- [Node Problem Detector](https://github.com/kubernetes/node-problem-detector)
- [Promtail](https://grafana.com/docs/loki/latest/send-data/promtail/)
- [Secret Reloader](https://github.com/stakater/Reloader)
- [Teslamate](https://github.com/teslamate-org/teslamate)
- [Transmission](https://github.com/transmission/transmission)
- [Uptime Kuma](https://github.com/louislam/uptime-kuma)
- [Vaultwarden](https://github.com/dani-garcia/vaultwarden)
- [cert-manager](https://github.com/cert-manager/cert-manager)
- [kubelet serving cert approver](https://github.com/alex1989hu/kubelet-serving-cert-approver)

## 🛠️ Changelog

Check the [commit history](https://github.com/nidr0x/k8s-gitops/commits/master)

## 🔗 External cloud dependencies

While most of my infrastructure and workloads are self-hosted I do rely upon the cloud for certain key parts of my setup. This saves me from having to worry about two things. (1) Dealing with chicken/egg scenarios and (2) services I critically need whether my cluster is online or not.

| Service                                   | Use                                                       | Cost                 |
| ----------------------------------------- | --------------------------------------------------------- | -------------------- |
| [Cloudflare](https://www.cloudflare.com/) | Domain & R2 (Terrafom backend) & Oauth (Using Zero Trust) | ~$10/yr              |
| [GitHub](https://www.github.com/)         | Repository                                                | Free                 |
| [Brevo](https://www.brevo.com/)           | SMTP email platform                                       | Free (up to 300/day) |
| [ZeroSSL](https://www.zerossl.com/)       | Issuing SSL Certificates via Cert Manager                 | Free                 |

## 📁 Repository structure

The repository is organized into folders by application. Each folder contains the necessary manifest files to deploy the application on a Kubernetes cluster. The `argocd` folder contains files for setting up and managing ArgoCD.
