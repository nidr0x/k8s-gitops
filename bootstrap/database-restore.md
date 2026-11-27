# Database restore

Restore the CloudNativePG databases from the Barman Cloud backups in R2.

> This procedure has not been run end to end yet. Run the [restore drill](#restore-drill) before relying on it.

## Databases

A _lineage_ is the `serverName` under which a cluster writes its base backups and WAL.

| Argo CD application          | Namespace         | Cluster                  | ObjectStore                 | Current lineage             |
| ---------------------------- | ----------------- | ------------------------ | --------------------------- | --------------------------- |
| `homeassistant`              | `homeassistant`   | `homeassistant-database` | `homeassistant-database-k2` | `homeassistant-database-k2` |
| `miniflux`                   | `miniflux`        | `miniflux-database`      | `miniflux-database-k2`      | `miniflux-database-k2`      |
| `n8n`                        | `n8n`             | `n8n-database`           | `n8n-database-k2`           | `n8n-database-k2`           |
| `teslamate`                  | `teslamate`       | `teslamate-database`     | `teslamate-database-k2`     | `teslamate-database-k2`     |
| `victoria-metrics-k8s-stack` | `kube-monitoring` | `grafana-database`       | `grafana-database-k2`       | `grafana-database-k2`       |
| `pocket-id`                  | `pocket-id`       | `pocket-id-database`     | `pocket-id-database`        | `pocket-id-database-pg18`   |

All of them live in the same R2 bucket, so there is no second copy. Retention is 7 days (3 for Grafana).

## The rule

CloudNativePG reads `bootstrap` when it creates a cluster. In Git, each cluster has:

- **Recovery source** (`spec.externalClusters`): the current lineage.
- **Archive target** (`spec.plugins`): the same lineage, because that is where the running cluster writes.

A cluster recreated from this state must not start: its archive target already holds data, and CloudNativePG stops with `Expected empty archive`. Before recreating it, change **only the archive target** to a new, never used `serverName`, such as `miniflux-database-r20261126`.

- Do not change the recovery source to an older lineage to get past an error. It restores old data.
- Do not set `cnpg.io/skipEmptyWalArchiveCheck`. It can overwrite the backups you are restoring from.
- Do not push a new archive target while the old cluster is still running. Argo CD would apply it to the live database.

## Before any restore

1. Confirm that R2 holds a recent base backup and WAL for the lineage. A manifest does not prove that a backup exists.
2. Have these available outside the cluster: the SOPS PGP private key, Doppler access (R2 credentials and application keys such as the Pocket ID and n8n encryption keys), and the Talos secrets.
3. Remember that Argo CD and Grafana sign in through Pocket ID. Keep `kubectl` access and a local admin login that do not depend on it.

## Restore drill

This restores a copy into a temporary namespace. The copy has no `spec.plugins`, so it does not archive WAL, and its ObjectStore has no retention policy. It uses the production R2 credentials, so delete the namespace when you finish.

Set the values from the table. `DB` and `OWNER` come from `bootstrap.recovery` in the cluster's `database.yaml`:

```bash
export NS=miniflux CLUSTER=miniflux-database STORE=miniflux-database-k2 LINEAGE=miniflux-database-k2 DB=miniflux OWNER=miniflux
```

Copy the ObjectStore and its credentials without printing them:

```bash
kubectl create namespace restore-drill
```

```bash
for SECRET in $(kubectl -n "$NS" get objectstores.barmancloud.cnpg.io "$STORE" -o json | jq -r '.spec.configuration.s3Credentials | .accessKeyId.name, .secretAccessKey.name' | sort -u); do
  kubectl -n "$NS" get secret "$SECRET" -o json |
    jq '{apiVersion, kind, type, data, metadata: {name: .metadata.name, namespace: "restore-drill"}}' |
    kubectl create -f -
done
```

```bash
kubectl -n "$NS" get objectstores.barmancloud.cnpg.io "$STORE" -o json |
  jq '{apiVersion, kind, metadata: {name: .metadata.name, namespace: "restore-drill"}, spec: (.spec | del(.retentionPolicy))}' |
  kubectl create -f -
```

Create the cluster with the same image and storage as production:

```bash
export IMAGE=$(kubectl -n "$NS" get clusters.postgresql.cnpg.io "$CLUSTER" -o jsonpath='{.spec.imageName}')
```

```bash
kubectl create -f - <<EOF
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: drill
  namespace: restore-drill
spec:
  instances: 1
  imageName: ${IMAGE}
  bootstrap:
    recovery:
      database: ${DB}
      owner: ${OWNER}
      source: origin
  externalClusters:
    - name: origin
      plugin:
        name: barman-cloud.cloudnative-pg.io
        parameters:
          barmanObjectName: ${STORE}
          serverName: ${LINEAGE}
  storage:
    storageClass: proxmox-k2-zfs
    size: 5Gi
  walStorage:
    storageClass: proxmox-k2-zfs
    size: 5Gi
EOF
```

```bash
kubectl -n restore-drill wait --for=condition=Ready clusters.postgresql.cnpg.io/drill --timeout=30m
```

`Ready` is not enough. Query data that you know, and check how recent it is:

```bash
kubectl -n restore-drill exec -it drill-1 -c postgres -- psql -d "$DB"
```

Record the date, the lineage, how long the restore took and the newest row you found. Then clean up, and check that no volume was left behind:

```bash
kubectl delete namespace restore-drill
```

```bash
kubectl get pv | grep restore-drill
```

## Restore after losing the whole cluster

Argo CD creates all the databases by itself, so prepare Git **before** [bootstrapping](README.md).

1. For all six clusters, set `spec.plugins[].parameters.serverName` to a new lineage. Leave `barmanObjectName` and `spec.externalClusters` unchanged.
2. Merge to `master`, then bootstrap.
3. Wait for each cluster to be `Ready`, then check its data and its application. Applications read the `<cluster>-app` secret; confirm that they can connect.
4. [Close the restore](#close-the-restore).

If you bootstrapped without step 1, the new clusters stop with `Expected empty archive`. Apply step 1, then delete the stuck `Cluster` so Argo CD recreates it. Check first that it is the new, empty one.

## Restore one database

> Deleting a `Cluster` also deletes its volumes, including any WAL that has not reached R2. Run the drill first. If the volumes still hold data you need, stop and preserve them.

1. Disable automatic sync on `argocd-apps-yaml` and then on the affected application. The first one would otherwise restore the setting on the second.
2. Stop the applications that write to the database.
3. Merge the new archive target (step 1 above) for this cluster only.
4. Delete the `Cluster`, then sync the application manually.
5. Wait for `Ready`, check the data, and start the applications again.
6. [Close the restore](#close-the-restore), and enable automatic sync again on both applications.

### Point in time

To stop before a bad change, add a target under `spec.bootstrap.recovery` in the same commit as the new archive target. Always include the time zone:

```yaml
recoveryTarget:
  targetTime: "2026-11-26T10:00:00Z"
```

The time must be inside the retention window, and there must be a transaction after it, or recovery fails.

## Close the restore

1. Take a backup of the new lineage right away; do not wait for the nightly one:

   ```bash
   kubectl create -f - <<EOF
   apiVersion: postgresql.cnpg.io/v1
   kind: Backup
   metadata:
     generateName: post-restore-
     namespace: ${NS}
   spec:
     cluster:
       name: ${CLUSTER}
     method: plugin
     pluginConfiguration:
       name: barman-cloud.cloudnative-pg.io
   EOF
   ```

2. Confirm that it reaches `completed`:

   ```bash
   kubectl -n "$NS" get backups.postgresql.cnpg.io
   ```

3. In a second commit, set `spec.externalClusters[].plugin.parameters.serverName` to the new lineage, and remove any `recoveryTarget`. Update the table above.

Without step 3, the next rebuild restores the state from before this restore.

Keep the previous lineage in R2 until the new one has passed a drill.

## References

- [CloudNativePG recovery](https://github.com/cloudnative-pg/cloudnative-pg/blob/release-1.28/docs/src/recovery.md)
- [Barman Cloud plugin usage](https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/)
