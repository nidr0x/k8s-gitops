"""Unit tests for the OpenSRE Alertmanager state machine."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("alertmanager-poller.py")


def load_module():
    """Load the hyphenated production module for isolated unit tests."""
    spec = importlib.util.spec_from_file_location("poller", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PollerStateMachineTest(unittest.TestCase):
    """Verify deduplication, health merging, and failure classification."""

    def test_success_is_deduplicated_and_failures_are_classified(self):
        """Deduplicate successes and classify provider failures."""
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module.STATE_FILE = root / "state.json"
            module.REPORT_DIR = root / "reports"
            module.HEALTH_FILE = root / "health.json"
            alert = {
                "fingerprint": "synthetic-one",
                "status": {"state": "active"},
                "labels": {"severity": "critical", "alertname": "SyntheticTest"},
                "annotations": {},
            }
            calls = []
            module.active_alerts = lambda: [alert]

            def succeed(value):
                calls.append(value["fingerprint"])
                report = module.REPORT_DIR / "synthetic.json"
                report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text("{}")
                return str(report)

            module.investigate = succeed
            module.run_once()
            module.run_once()
            state = module.load_state()
            self.assertEqual(calls, ["synthetic-one"])
            self.assertIn("synthetic-one", state["completed"])

            module.write_health(first=True)
            module.write_health(second=True)
            health = json.loads(module.HEALTH_FILE.read_text())
            self.assertTrue(health["first"])
            self.assertTrue(health["second"])

            alert["fingerprint"] = "synthetic-two"
            module.investigate = lambda value: (_ for _ in ()).throw(
                RuntimeError("HTTP 402 Insufficient Balance")
            )
            module.run_once()
            state = module.load_state()
            self.assertEqual(
                state["failures"]["synthetic-two"]["last_error_kind"],
                "provider_balance",
            )


if __name__ == "__main__":
    unittest.main()
