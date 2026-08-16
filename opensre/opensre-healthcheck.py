#!/usr/bin/env python3
"""Fail fast when the OpenSRE trigger or its Alertmanager dependency is unhealthy."""

# The filename is part of the systemd deployment contract.
# pylint: disable=invalid-name

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

HEALTH_FILE = Path(
    os.environ.get("OPENSRE_HEALTH_FILE", "/home/carlos/opensre/health.json")
)
MAX_AGE_SECONDS = int(os.environ.get("OPENSRE_HEALTH_MAX_AGE_SECONDS", "120"))
ALERTMANAGER_URL = os.environ.get("OPENSRE_ALERTMANAGER_URL", "http://127.0.0.1:9093")


def service_is_active(name: str) -> bool:
    """Return whether a systemd service is active."""
    return (
        subprocess.run(
            ["systemctl", "is-active", "--quiet", name], check=False
        ).returncode
        == 0
    )


def parse_time(value: str) -> datetime:
    """Parse an ISO 8601 timestamp, including a trailing Z."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    """Check the OpenSRE services, Alertmanager, and poller health state."""
    failures: list[str] = []
    if not service_is_active("alertmanager-port-forward.service"):
        failures.append("alertmanager-port-forward.service is not active")
    if not service_is_active("opensre-alertmanager.service"):
        failures.append("opensre-alertmanager.service is not active")

    try:
        with urlopen(  # noqa: S310 - URL is local configuration
            f"{ALERTMANAGER_URL}/-/ready", timeout=5
        ) as response:
            if response.status != 200:
                failures.append(
                    f"Alertmanager readiness returned HTTP {response.status}"
                )
    except OSError as error:
        failures.append(f"Alertmanager readiness failed: {error}")

    try:
        health = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
        updated_at = parse_time(health["updated_at"])
        age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        if age > MAX_AGE_SECONDS:
            failures.append(f"health.json is {int(age)} seconds old")
        if health.get("poll_status") != "ok":
            failures.append(f"poll status is {health.get('poll_status', 'missing')}")
        if health.get("failed_investigations", 0):
            failures.append(
                f"{health['failed_investigations']} investigation(s) are failing"
            )
    except (
        FileNotFoundError,
        KeyError,
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        failures.append(f"health.json cannot be read: {error}")

    if failures:
        print("; ".join(failures), file=sys.stderr)
        return 1
    print("OpenSRE health check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
