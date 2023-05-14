# Homelab Repository

This repository contains Kubernetes manifests and ArgoCD definitions for a homelab managed by ArgoCD. It includes a variety of applications organized into folders by application.

## Application list

- [Adguard Home](https://github.com/AdguardTeam/AdGuardHome)
- [ArgoCD](https://github.com/argoproj/argo-cd)
- [Cert-manager](https://github.com/cert-manager/cert-manager)
- [Cloudflare DDNS Updater](https://github.com/nidr0x/cloudflare-ddns-updater)
- [CSI Driver NFS](https://github.com/kubernetes-csi/csi-driver-nfs)
- [External DNS](https://github.com/kubernetes-sigs/external-dns)
- [External Secrets](https://github.com/external-secrets/external-secrets)
- [FreshRSS](https://github.com/FreshRSS/FreshRSS)
- [GPhotos Sync](https://github.com/gilesknap/gphotos-sync)
- [Home Assistant](https://github.com/home-assistant/docker)
- [Kube Prometheus Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack)
- [Kubernetes Reflector](https://github.com/emberstack/kubernetes-reflector)
- [Node Problem Detector](https://github.com/kubernetes/node-problem-detector)
- [OAuth2 Proxy](https://github.com/oauth2-proxy/oauth2-proxy)
- [Secret Reloader](https://github.com/stakater/Reloader)
- [SNMP Exporter](https://github.com/prometheus/snmp_exporter)
- [Transmission](https://github.com/transmission/transmission)
- [Uptime Kuma](https://github.com/louislam/uptime-kuma)
- [Vaultwarden](https://github.com/dani-garcia/vaultwarden)

## Changelog

Check the [commit history](https://github.com/nidr0x/homelab/commits/master)

## Repository Structure

The repository is organized into folders by application. Each folder contains the necessary manifest files to deploy the application on a Kubernetes cluster. The `argocd` folder contains files for setting up and managing ArgoCD.
