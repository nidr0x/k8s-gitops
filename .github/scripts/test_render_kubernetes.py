"""Focused tests for the Argo CD source resolver."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import render_kubernetes
import yaml


class RenderKubernetesTest(unittest.TestCase):
    """Cover source parsing, local paths, SOPS detection, and chart failures."""

    def test_application_sources_supports_single_and_multi_source_apps(self):
        """Read both source forms used by Argo CD Applications."""
        self.assertEqual(
            render_kubernetes.application_sources({"source": {"chart": "cilium"}}),
            [{"chart": "cilium"}],
        )
        self.assertEqual(
            render_kubernetes.application_sources({"sources": [{"chart": "cilium"}]}),
            [{"chart": "cilium"}],
        )

    def test_resolves_value_files_from_local_source_ref(self):
        """Resolve a value file from a local repository source ref."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            values = root / "kubernetes/main/apps/cilium/values.yaml"
            values.parent.mkdir(parents=True)
            values.write_text("routingMode: native\n", encoding="utf-8")
            chart = {"repoURL": "https://helm.cilium.io"}
            refs = {"repo": {"repoURL": render_kubernetes.REPOSITORY_URL}}

            self.assertEqual(
                render_kubernetes.resolve_value_file(
                    root, chart, refs, "$repo/kubernetes/main/apps/cilium/values.yaml"
                ),
                values.resolve(),
            )

    def test_rejects_value_files_that_escape_repository(self):
        """Reject value file paths that leave the checkout."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            chart = {"repoURL": "https://helm.cilium.io"}
            refs = {"repo": {"repoURL": render_kubernetes.REPOSITORY_URL}}

            with self.assertRaises(ValueError):
                render_kubernetes.resolve_value_file(
                    root, chart, refs, "$repo/../../outside.yaml"
                )

    def test_detects_sops_documents_without_printing_values(self):
        """Identify encrypted documents while leaving plaintext Secrets valid."""
        self.assertTrue(
            render_kubernetes.is_sops_document({"sops": {"mac": "ENC[redacted]"}})
        )
        self.assertTrue(
            render_kubernetes.is_sops_document(
                {"apiVersion": "ENC[redacted]", "kind": "ENC[redacted]"}
            )
        )
        self.assertFalse(
            render_kubernetes.is_sops_document({"apiVersion": "v1", "kind": "Secret"})
        )

    def test_helm_render_failure_does_not_skip_later_sources(self):
        """Continue attempting later Argo CD charts after a render failure."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            apps = root / "argocd/apps"
            apps.mkdir(parents=True)
            for name, chart in (("first", "broken"), ("second", "valid")):
                app = {
                    "apiVersion": "argoproj.io/v1alpha1",
                    "kind": "Application",
                    "metadata": {"name": name},
                    "spec": {
                        "destination": {"namespace": "default"},
                        "source": {
                            "repoURL": "https://charts.example",
                            "chart": chart,
                            "targetRevision": "1.0.0",
                        },
                    },
                }
                (apps / f"{name}.yaml").write_text(
                    yaml.safe_dump(app), encoding="utf-8"
                )

            with (
                patch("render_kubernetes.ROOT", root),
                patch(
                    "render_kubernetes.render_helm_chart",
                    side_effect=[RuntimeError("render failed"), 0],
                ) as render_chart,
            ):
                self.assertEqual(
                    render_kubernetes.render_helm_sources("1.37.2", []),
                    (0, 0, ["first/broken@1.0.0"]),
                )
            self.assertEqual(render_chart.call_count, 2)


if __name__ == "__main__":
    unittest.main()
