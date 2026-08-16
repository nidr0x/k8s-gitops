#!/usr/bin/env python3
"""Trigger one OpenSRE investigation for each newly firing Alertmanager alert."""

# The filename is part of the systemd deployment contract. The poll loop is
# intentionally stateful and coordinates several pieces of incident metadata.
# pylint: disable=invalid-name,redefined-builtin,too-many-locals,too-many-statements

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

ALERTMANAGER_URL = os.environ.get("OPENSRE_ALERTMANAGER_URL", "http://127.0.0.1:9093")
POLL_SECONDS = int(os.environ.get("OPENSRE_ALERTMANAGER_POLL_SECONDS", "30"))
SEVERITIES = {
    value.strip().lower()
    for value in os.environ.get("OPENSRE_ALERT_SEVERITIES", "warning,critical").split(
        ","
    )
    if value.strip()
}
INVESTIGATION_TIMEOUT = int(
    os.environ.get("OPENSRE_INVESTIGATION_TIMEOUT_SECONDS", "900")
)
MAX_CONCURRENCY = int(os.environ.get("OPENSRE_ALERT_MAX_CONCURRENCY", "2"))
STATE_FILE = Path(
    os.environ.get("OPENSRE_ALERT_STATE", "/home/carlos/opensre/alert-state.json")
)
REPORT_DIR = Path(
    os.environ.get("OPENSRE_REPORT_DIR", "/home/carlos/opensre/incidents")
)
HEALTH_FILE = Path(
    os.environ.get("OPENSRE_HEALTH_FILE", "/home/carlos/opensre/health.json")
)
OPENSRE_BIN = os.environ.get("OPENSRE_BIN", "/home/carlos/.local/bin/opensre")
RETRY_SECONDS = int(os.environ.get("OPENSRE_RETRY_SECONDS", "300"))
MAX_RETRY_SECONDS = int(os.environ.get("OPENSRE_MAX_RETRY_SECONDS", "3600"))
REPORT_RETENTION_DAYS = int(os.environ.get("OPENSRE_REPORT_RETENTION_DAYS", "30"))
WEBHOOK_ENABLED = os.environ.get("OPENSRE_WEBHOOK_ENABLED", "false").lower() == "true"
WEBHOOK_BIND = os.environ.get("OPENSRE_WEBHOOK_BIND", "0.0.0.0")
WEBHOOK_PORT = int(os.environ.get("OPENSRE_WEBHOOK_PORT", "9094"))
WEBHOOK_PATH = os.environ.get("OPENSRE_WEBHOOK_PATH", "/alertmanager")
WEBHOOK_TOKEN = os.environ.get("OPENSRE_WEBHOOK_TOKEN", "")
MAX_WEBHOOK_BODY = int(os.environ.get("OPENSRE_MAX_WEBHOOK_BODY", str(2 * 1024 * 1024)))
WEBHOOK_WAKE = threading.Event()


def active_alerts() -> list[dict]:
    """Return active alerts matching the configured severities."""
    request = Request(f"{ALERTMANAGER_URL}/api/v2/alerts?active=true")
    # Alertmanager URL is local service configuration.
    with urlopen(request, timeout=10) as response:  # noqa: S310
        payload = json.load(response)
    return [
        alert
        for alert in payload
        if alert.get("status", {}).get("state") == "active"
        and alert.get("labels", {}).get("severity", "").lower() in SEVERITIES
        and alert.get("labels", {}).get("alertname")
        not in {"Watchdog", "InfoInhibitor"}
    ]


def load_state() -> dict:
    """Load persisted alert state, returning an empty state if unavailable."""
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {
            "active": set(state.get("active", [])),
            "completed": set(state.get("completed", [])),
            "failures": (
                state.get("failures", {})
                if isinstance(state.get("failures", {}), dict)
                else {}
            ),
            "running": (
                state.get("running", {})
                if isinstance(state.get("running", {}), dict)
                else {}
            ),
        }
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"active": set(), "completed": set(), "failures": {}, "running": {}}


def save_state(state: dict) -> None:
    """Persist alert state atomically."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            {
                "active": sorted(state["active"]),
                "completed": sorted(state["completed"]),
                "failures": state["failures"],
                "running": state["running"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(STATE_FILE)


def write_health(**values: object) -> None:
    """Merge health values into the health file and update its timestamp."""
    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = HEALTH_FILE.with_suffix(".tmp")
    try:
        current = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        current = {}
    current.update(values)
    current["updated_at"] = datetime.now(timezone.utc).isoformat()
    temporary.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    temporary.replace(HEALTH_FILE)


def iso_now() -> str:
    """Return the current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def retry_delay(attempts: int) -> int:
    """Return the capped exponential delay for a failed investigation."""
    return min(RETRY_SECONDS * (2 ** max(attempts - 1, 0)), MAX_RETRY_SECONDS)


def error_kind(error: Exception) -> str:
    """Classify a failure for health reporting and operator triage."""
    message = str(error)
    if "Insufficient Balance" in message or "402" in message:
        return "provider_balance"
    if "timed out" in message.lower() or "timeout" in message.lower():
        return "timeout"
    return "investigation"


def compact_error(error: Exception) -> str:
    """Extract a concise, useful message from a command failure."""
    lines = [line.strip() for line in str(error).splitlines() if line.strip()]
    if not lines:
        return error.__class__.__name__
    relevant = next(
        (
            line
            for line in reversed(lines)
            if "error code" in line.lower()
            or "insufficient balance" in line.lower()
            or "timed out" in line.lower()
        ),
        lines[-1],
    )
    return relevant[-500:]


def prune_reports() -> None:
    """Remove incident reports older than the configured retention period."""
    cutoff = time.time() - REPORT_RETENTION_DAYS * 86400
    for report in REPORT_DIR.glob("*.json"):
        try:
            if report.stat().st_mtime < cutoff:
                report.unlink()
        except FileNotFoundError:
            continue


def investigate(alert: dict) -> str:
    """Run OpenSRE for one Alertmanager alert and return its report path."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fingerprint = alert.get("fingerprint", "unknown")
    payload = {
        "version": "4",
        "groupKey": fingerprint,
        "status": "firing",
        "receiver": "opensre",
        "groupLabels": alert.get("labels", {}),
        "commonLabels": alert.get("labels", {}),
        "commonAnnotations": alert.get("annotations", {}),
        "alerts": [alert],
    }
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report = REPORT_DIR / f"{timestamp}-{fingerprint}.json"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as input_file:
        json.dump(payload, input_file)
        input_path = input_file.name
    try:
        result = subprocess.run(
            [
                OPENSRE_BIN,
                "investigate",
                "--input",
                input_path,
                "--output",
                str(report),
            ],
            timeout=INVESTIGATION_TIMEOUT,
            env={**os.environ, "NO_COLOR": "1"},
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            detail = (result.stderr or result.stdout or "").strip()
            raise RuntimeError(
                detail[-1000:] or f"opensre exited with status {result.returncode}"
            )
        return str(report)
    except Exception:  # pylint: disable=broad-exception-caught
        report.unlink(missing_ok=True)
        raise
    finally:
        Path(input_path).unlink(missing_ok=True)


def run_once() -> None:
    """Poll Alertmanager and process newly firing alerts."""
    prune_reports()
    alerts = active_alerts()
    current = {alert["fingerprint"] for alert in alerts if alert.get("fingerprint")}
    state = load_state()
    now = time.time()
    state["active"] = current
    state["completed"] &= current
    state["failures"] = {
        fingerprint: failure
        for fingerprint, failure in state["failures"].items()
        if fingerprint in current
    }

    stale_errors = []
    for fingerprint, running in list(state["running"].items()):
        if fingerprint not in current:
            state["running"].pop(fingerprint, None)
            continue
        started_at = float(running.get("started_at", 0))
        if started_at and now - started_at > INVESTIGATION_TIMEOUT + 60:
            attempts = int(running.get("attempt", 1))
            message = "investigation abandoned after poller restart or timeout"
            state["running"].pop(fingerprint, None)
            state["failures"][fingerprint] = {
                "attempts": attempts,
                "next_retry": now + retry_delay(attempts),
                "last_error": message,
                "last_error_kind": "stale_investigation",
                "last_failure_at": iso_now(),
            }
            stale_errors.append(message)

    candidates = []
    for alert in alerts:
        fingerprint = alert.get("fingerprint")
        if (
            not fingerprint
            or fingerprint in state["completed"]
            or fingerprint in state["running"]
        ):
            continue
        failure = state["failures"].get(fingerprint)
        if fingerprint not in state["failures"] or now >= failure.get("next_retry", 0):
            candidates.append(alert)

    # Persist the claim before launching work, so a restart can recover stale work.
    for alert in candidates:
        fingerprint = alert["fingerprint"]
        previous = state["failures"].get(fingerprint, {})
        state["running"][fingerprint] = {
            "started_at": now,
            "attempt": int(previous.get("attempts", 0)) + 1,
            "alertname": alert.get("labels", {}).get("alertname", "unknown"),
        }
    save_state(state)
    health = {
        "poll_status": "ok",
        "last_poll_success_at": iso_now(),
        "active_alerts": len(current),
        "queued": len(candidates),
        "in_flight": len(state["running"]),
        "failed_investigations": len(state["failures"]),
    }
    if state["failures"]:
        latest_fingerprint, latest_failure = max(
            state["failures"].items(),
            key=lambda item: item[1].get("last_failure_at", ""),
        )
        health.update(
            last_error=latest_failure.get("last_error", "investigation failed"),
            last_error_kind=latest_failure.get("last_error_kind", "investigation"),
            last_failure_at=latest_failure.get("last_failure_at"),
            last_failure_fingerprint=latest_fingerprint,
        )
    if stale_errors:
        health["last_error"] = stale_errors[-1]
        health["last_error_kind"] = "stale_investigation"
    write_health(**health)

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as executor:
        futures = {executor.submit(investigate, alert): alert for alert in candidates}
        for future in as_completed(futures):
            alert = futures[future]
            fingerprint = alert["fingerprint"]
            running = state["running"].pop(fingerprint, {})
            try:
                report = future.result()
            except Exception as error:  # pylint: disable=broad-exception-caught
                attempts = int(running.get("attempt", 1))
                failure = {
                    "attempts": attempts,
                    "next_retry": time.time() + retry_delay(attempts),
                    "last_error": compact_error(error),
                    "last_error_kind": error_kind(error),
                    "last_failure_at": iso_now(),
                }
                state["failures"][fingerprint] = failure
                write_health(
                    active_alerts=len(current),
                    queued=0,
                    in_flight=len(state["running"]),
                    failed_investigations=len(state["failures"]),
                    last_error=failure["last_error"],
                    last_error_kind=failure["last_error_kind"],
                    last_failure_at=failure["last_failure_at"],
                    last_failure_fingerprint=fingerprint,
                )
            else:
                state["completed"].add(fingerprint)
                state["failures"].pop(fingerprint, None)
                write_health(
                    last_successful_investigation_at=iso_now(), last_report=report
                )
            save_state(state)
    write_health(
        active_alerts=len(current),
        queued=0,
        in_flight=len(state["running"]),
        failed_investigations=len(state["failures"]),
    )


class WebhookHandler(BaseHTTPRequestHandler):
    """Accept authenticated Alertmanager wake-up notifications."""

    def do_POST(self) -> None:  # noqa: N802 - stdlib HTTP handler API
        """Validate a webhook request and wake the polling loop."""
        if self.path != WEBHOOK_PATH:
            self.send_error(404)
            return
        supplied = self.headers.get("Authorization", "")
        expected = f"Bearer {WEBHOOK_TOKEN}"
        if not WEBHOOK_TOKEN or supplied != expected:
            self.send_error(401)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400)
            return
        if length <= 0 or length > MAX_WEBHOOK_BODY:
            self.send_error(413)
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, OSError):
            self.send_error(400)
            return
        if not isinstance(payload, dict) or not isinstance(
            payload.get("alerts", []), list
        ):
            self.send_error(400)
            return
        WEBHOOK_WAKE.set()
        self.send_response(202)
        self.end_headers()

    def log_message(
        self,
        format: str,
        *args: object,
    ) -> None:
        """Write HTTP access logs to the service journal."""
        print(f"webhook: {format % args}", flush=True)


def start_webhook() -> ThreadingHTTPServer | None:
    """Start the authenticated webhook listener when enabled."""
    if not WEBHOOK_ENABLED:
        return None
    if not WEBHOOK_TOKEN:
        raise RuntimeError(
            "OPENSRE_WEBHOOK_TOKEN is required when webhook mode is enabled"
        )
    server = ThreadingHTTPServer((WEBHOOK_BIND, WEBHOOK_PORT), WebhookHandler)
    thread = threading.Thread(
        target=server.serve_forever, name="alertmanager-webhook", daemon=True
    )
    thread.start()
    print(
        f"webhook listening on {WEBHOOK_BIND}:{WEBHOOK_PORT}{WEBHOOK_PATH}", flush=True
    )
    return server


def main() -> None:
    """Run the Alertmanager watcher until the service is stopped."""
    server = start_webhook()
    while True:
        try:
            run_once()
        except Exception as error:  # pylint: disable=broad-exception-caught
            print(f"alertmanager poll failed: {error}", flush=True)
            write_health(
                poll_status="error",
                last_error=str(error)[:500],
                last_error_kind="alertmanager_poll",
                last_poll_error_at=iso_now(),
            )
        WEBHOOK_WAKE.wait(POLL_SECONDS)
        WEBHOOK_WAKE.clear()

    if server is not None:
        server.shutdown()


if __name__ == "__main__":
    main()
