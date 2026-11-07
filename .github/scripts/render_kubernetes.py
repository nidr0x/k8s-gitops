#!/usr/bin/env python3
"""Render repository Kustomize sources and Argo CD Helm chart sources."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_URL = "https://github.com/nidr0x/k8s-gitops"
KUSTOMIZE_ROOTS = (ROOT / "kubernetes/main/apps", ROOT / "argocd")


def kubernetes_version() -> str:
    config = ROOT / "talos/topf.yaml"
    try:
        talos = yaml.safe_load(config.read_text(encoding="utf-8"))
        version = str(talos["kubernetesVersion"]).removeprefix("v")
    except (OSError, KeyError, TypeError, yaml.YAMLError) as error:
        raise RuntimeError(
            "Could not read kubernetesVersion from talos/topf.yaml"
        ) from error
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError("talos/topf.yaml must set a pinned Kubernetes version")
    return version


def repository_source(source: dict[str, Any]) -> bool:
    url = str(source.get("repoURL", "")).rstrip("/").removesuffix(".git")
    return url == REPOSITORY_URL


def application_sources(spec: dict[str, Any]) -> list[dict[str, Any]]:
    sources = spec.get("sources")
    if isinstance(sources, list):
        return [source for source in sources if isinstance(source, dict)]
    source = spec.get("source")
    return [source] if isinstance(source, dict) else []


def resolve_value_file(
    root: Path,
    chart_source: dict[str, Any],
    ref_sources: dict[str, dict[str, Any]],
    value_file: str,
) -> Path:
    if value_file.startswith("$"):
        match = re.fullmatch(r"\$([^/]+)/(.+)", value_file)
        if not match:
            raise ValueError("Argo CD valueFiles ref must use $ref/path syntax")
        ref, relative = match.groups()
        source = ref_sources.get(ref)
        if source is None or not repository_source(source):
            raise ValueError(
                f"Argo CD valueFiles ref {ref!r} is not a local repository source"
            )
        base = root / str(source.get("path", ""))
    else:
        if not repository_source(chart_source):
            raise ValueError(
                "External Helm chart valueFiles must use a local Argo CD source ref"
            )
        relative = value_file
        base = root / str(chart_source.get("path", ""))

    resolved = (base / relative).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Argo CD valueFiles path escapes the checkout")
    if not resolved.is_file():
        raise ValueError(f"Argo CD valueFiles entry does not exist: {relative}")
    return resolved


def is_sops_document(document: Any) -> bool:
    if not isinstance(document, dict):
        return False
    if "sops" in document:
        return True
    return any(
        isinstance(document.get(field), str) and document[field].startswith("ENC[")
        for field in ("apiVersion", "kind")
    )


def run(command: list[str], description: str) -> str:
    result = subprocess.run(
        command, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(f"{description} failed (exit {result.returncode})")
    return result.stdout


def add_yaml_documents(source: str, origin: str, rendered: list[dict[str, Any]]) -> int:
    skipped = 0
    try:
        documents = yaml.safe_load_all(source)
        for document in documents:
            if document is None:
                continue
            if is_sops_document(document):
                skipped += 1
                continue
            if (
                not isinstance(document, dict)
                or "apiVersion" not in document
                or "kind" not in document
            ):
                raise RuntimeError(
                    f"Rendered document from {origin} is not a Kubernetes resource"
                )
            rendered.append(document)
    except yaml.YAMLError as error:
        raise RuntimeError(f"Could not parse rendered YAML from {origin}") from error
    return skipped


def render_kustomize(version: str, rendered: list[dict[str, Any]]) -> tuple[int, int]:
    count = 0
    skipped = 0
    directories = sorted(
        path.parent
        for root in KUSTOMIZE_ROOTS
        if root.exists()
        for path in root.rglob("kustomization.yaml")
    )
    for directory in directories:
        output = run(
            [
                "kubectl",
                "kustomize",
                str(directory),
                "--enable-helm",
                "--helm-kube-version",
                version,
                "--load-restrictor",
                "LoadRestrictionsNone",
            ],
            f"Kustomize build for {directory.relative_to(ROOT)}",
        )
        before = len(rendered)
        skipped += add_yaml_documents(
            output, str(directory.relative_to(ROOT)), rendered
        )
        count += len(rendered) - before
    return count, skipped


def helm_repository(repo_url: str, app_name: str, repo_cache: dict[str, str]) -> str:
    if repo_url.startswith("oci://") or not repo_url.startswith(
        ("https://", "http://")
    ):
        return f"oci://{repo_url.removeprefix('oci://').rstrip('/')}"

    repo_name = repo_cache.get(repo_url)
    if repo_name is None:
        suffix = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:10]
        repo_name = f"ci-{suffix}"
        run(
            ["helm", "repo", "add", repo_name, repo_url, "--force-update"],
            f"Adding Helm repository for {app_name}",
        )
        repo_cache[repo_url] = repo_name
    return repo_name


def render_helm_chart(
    root: Path,
    app_name: str,
    namespace: str,
    source: dict[str, Any],
    ref_sources: dict[str, dict[str, Any]],
    version: str,
    repo_cache: dict[str, str],
    rendered: list[dict[str, Any]],
) -> int:
    chart = source.get("chart")
    chart_version = source.get("targetRevision")
    repo_url = source.get("repoURL")
    if not all(
        isinstance(value, str) and value for value in (chart, chart_version, repo_url)
    ):
        raise RuntimeError(
            f"Argo CD Helm source for {app_name} must pin repoURL, chart, and targetRevision"
        )

    helm = source.get("helm") or {}
    if not isinstance(helm, dict):
        raise RuntimeError(f"Argo CD Helm settings for {app_name} must be a mapping")
    repository = helm_repository(repo_url, app_name, repo_cache)
    chart_ref = f"{repository}/{chart}"
    command = [
        "helm",
        "template",
        str(helm.get("releaseName") or app_name),
        chart_ref,
        "--version",
        chart_version,
        "--kube-version",
        version,
        "--namespace",
        str(helm.get("namespace") or namespace),
    ]
    if not helm.get("skipCrds", False):
        command.append("--include-crds")
    # Check rendered resources with Kubeconform, not upstream chart value schemas.
    command.append("--skip-schema-validation")
    for api_version in helm.get("apiVersions", []):
        command.extend(("--api-versions", str(api_version)))

    with tempfile.TemporaryDirectory(prefix="k8s-gitops-helm-") as temp_dir:
        temp_root = Path(temp_dir)
        value_files = helm.get("valueFiles", [])
        if not isinstance(value_files, list):
            raise RuntimeError(f"Argo CD valueFiles for {app_name} must be a list")
        for value_file in value_files:
            resolved = resolve_value_file(root, source, ref_sources, str(value_file))
            command.extend(("--values", str(resolved)))

        values = helm.get("values")
        if isinstance(values, str) and values.strip():
            values_path = temp_root / "values.yaml"
            values_path.write_text(values, encoding="utf-8")
            command.extend(("--values", str(values_path)))
        values_object = helm.get("valuesObject")
        if isinstance(values_object, dict):
            values_path = temp_root / "values-object.yaml"
            values_path.write_text(
                yaml.safe_dump(values_object, sort_keys=False), encoding="utf-8"
            )
            command.extend(("--values", str(values_path)))

        for parameter in helm.get("parameters", []):
            if (
                not isinstance(parameter, dict)
                or not parameter.get("name")
                or "value" not in parameter
            ):
                raise RuntimeError(
                    f"Invalid Helm parameter in Argo CD application {app_name}"
                )
            option = "--set-string" if parameter.get("forceString", False) else "--set"
            command.extend((option, f"{parameter['name']}={parameter['value']}"))

        for parameter in helm.get("fileParameters", []):
            if (
                not isinstance(parameter, dict)
                or not parameter.get("name")
                or not parameter.get("path")
            ):
                raise RuntimeError(
                    f"Invalid Helm fileParameter in Argo CD application {app_name}"
                )
            path = resolve_value_file(root, source, ref_sources, str(parameter["path"]))
            command.extend(("--set-file", f"{parameter['name']}={path}"))

        output = run(command, f"Helm render for {app_name}/{chart}@{chart_version}")
    return add_yaml_documents(output, f"{app_name}/{chart}", rendered)


def render_helm_sources(
    version: str, rendered: list[dict[str, Any]]
) -> tuple[int, int, list[str]]:
    rendered_count = 0
    skipped = 0
    failures: list[str] = []
    repo_cache: dict[str, str] = {}
    for app_path in sorted((ROOT / "argocd/apps").glob("*.yaml")):
        try:
            app = yaml.safe_load(app_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            raise RuntimeError(
                f"Could not read Argo CD application {app_path.relative_to(ROOT)}"
            ) from error
        if not isinstance(app, dict) or app.get("kind") != "Application":
            continue
        spec = app.get("spec") or {}
        sources = application_sources(spec)
        references = {
            str(source["ref"]): source
            for source in sources
            if isinstance(source.get("ref"), str)
        }
        namespace = str((spec.get("destination") or {}).get("namespace") or "default")
        name = str((app.get("metadata") or {}).get("name") or app_path.stem)
        for source in sources:
            if "chart" not in source:
                continue
            before = len(rendered)
            chart = source.get("chart")
            revision = source.get("targetRevision")
            try:
                skipped += render_helm_chart(
                    ROOT,
                    name,
                    namespace,
                    source,
                    references,
                    version,
                    repo_cache,
                    rendered,
                )
            except (OSError, RuntimeError, ValueError, yaml.YAMLError):
                failures.append(f"{name}/{chart}@{revision}")
                continue
            rendered_count += len(rendered) - before
    return rendered_count, skipped, failures


def render_argocd_manifests(rendered: list[dict[str, Any]]) -> int:
    skipped = 0
    paths = [
        *(ROOT / "argocd/apps").glob("*.yaml"),
        *(ROOT / "argocd/setup").glob("*.yaml"),
    ]
    for path in sorted(paths):
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            raise RuntimeError(
                f"Could not read Argo CD manifest {path.relative_to(ROOT)}"
            ) from error
        skipped += add_yaml_documents(source, str(path.relative_to(ROOT)), rendered)
    return skipped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    try:
        version = kubernetes_version()
        rendered: list[dict[str, Any]] = []
        kustomize_count, encrypted_kustomize = render_kustomize(version, rendered)
        helm_count, encrypted_helm, helm_failures = render_helm_sources(
            version, rendered
        )
        encrypted_argocd = render_argocd_manifests(rendered)
        if not rendered:
            raise RuntimeError("No Kubernetes resources were rendered")

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as output:
            for document in rendered:
                yaml.safe_dump(document, output, sort_keys=False, explicit_start=True)

        if args.github_output:
            with args.github_output.open("a", encoding="utf-8") as output:
                output.write(f"kubernetes_version={version}\n")
        print(
            f"Rendered {kustomize_count} Kustomize and {helm_count} Helm resources; "
            f"excluded {encrypted_kustomize + encrypted_helm + encrypted_argocd} SOPS-encrypted documents."
        )
        if helm_failures:
            print(
                f"Failed to render Helm sources: {', '.join(helm_failures)}",
                file=sys.stderr,
            )
            return 1
    except (OSError, RuntimeError, ValueError, yaml.YAMLError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
