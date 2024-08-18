<div align="center">

[![Super-Linter](https://github.com/nidr0x/homelab/actions/workflows/lint.yaml/badge.svg)](https://github.com/marketplace/actions/super-linter)

# nidr0x Homelab 🏡

Welcome to the nidr0x Homelab repository! Here you'll find [Kubernetes](https://kubernetes.io/) manifests and [Argo CD](https://argoproj.github.io/cd/) definitions for a homelab environment, all running on top of [Talos](https://talos.dev). This setup includes a wide range of applications, each organized into its own folder, with versioning expertly managed by [Renovate](https://www.mend.io/renovate/).

</div>

## Application list

- [Adguard Home](https://github.com/AdguardTeam/AdGuardHome)
- [ArgoCD](https://github.com/argoproj/argo-cd)
- [CSI Driver NFS](https://github.com/kubernetes-csi/csi-driver-nfs)
- [Cert-manager](https://github.com/cert-manager/cert-manager)
- [Cloudflare DDNS Updater](https://github.com/nidr0x/cloudflare-ddns-updater)
- [External DNS](https://github.com/kubernetes-sigs/external-dns)
- [External Secrets](https://github.com/external-secrets/external-secrets)
- [FreshRSS](https://github.com/FreshRSS/FreshRSS)
- [GPhotos Sync](https://github.com/gilesknap/gphotos-sync)
- [Home Assistant](https://github.com/home-assistant/docker)
- [Kube Prometheus Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Node Problem Detector](https://github.com/kubernetes/node-problem-detector)
- [Secret Reloader](https://github.com/stakater/Reloader)
- [Teslamate](https://github.com/teslamate-org/teslamate)
- [Transmission](https://github.com/transmission/transmission)
- [Uptime Kuma](https://github.com/louislam/uptime-kuma)
- [Vaultwarden](https://github.com/dani-garcia/vaultwarden)

## Changelog

Check the [commit history](https://github.com/nidr0x/homelab/commits/master)

## Repository structure

The repository is organized into folders by application. Each folder contains the necessary manifest files to deploy the application on a Kubernetes cluster. The `argocd` folder contains files for setting up and managing ArgoCD.

WIP
