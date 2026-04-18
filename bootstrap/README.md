# Bootstrap

This repository keeps Day-0 intentionally small:

1. bootstrap Talos
2. label one control-plane node for Argo CD bootstrap scheduling
3. install Argo CD core directly
4. apply the app-of-apps objects
5. let Argo CD reconcile `cilium` first and wait for the `cilium` Argo CD application to become synced and non-degraded
6. remove the temporary bootstrap label after Cilium is healthy
7. restart Argo CD core so it re-schedules onto the normal node pool
8. print a post-bootstrap summary

## Prerequisites

- `kubectl` points at the target cluster
- `kustomize` is installed locally
- Argo CD bootstrap secrets are available locally at:
  - `argocd/secret.yaml.dec`

`argocd/secret.yaml.dec` is intentionally local-only and must not be committed.

## Commands

Use one control-plane node as the temporary bootstrap target. By default the tasks use `controlplane-01`.

Full Talos + Argo bootstrap:

```bash
task bootstrap:e2e BOOTSTRAP_NODE=controlplane-01
```

Argo-only handoff after Talos is already bootstrapped:

```bash
task bootstrap:argocd BOOTSTRAP_NODE=controlplane-01
```

If you want to run the steps individually:

```bash
task bootstrap:label-argocd-node BOOTSTRAP_NODE=controlplane-01
task bootstrap:apply-argocd-core
task bootstrap:apply-argocd-apps
task bootstrap:wait-cilium BOOTSTRAP_NODE=controlplane-01
task bootstrap:unlabel-argocd-node BOOTSTRAP_NODE=controlplane-01
task bootstrap:rebalance-argocd
task bootstrap:summary
```

## Why This Exists

Talos nodes using `cni: none` remain `NotReady` until Cilium is installed. The bootstrap label and Argo CD control-plane tolerations give Argo CD a narrow escape hatch so it can reconcile `cilium` without making the rest of the cluster permanently schedulable on control planes.

After the label is removed, `task bootstrap:rebalance-argocd` restarts the Argo CD core workloads so they are re-evaluated by the scheduler against the normal worker pool instead of simply staying where they first landed.
