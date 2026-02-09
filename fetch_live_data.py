#!/usr/bin/env python3
"""
BRHAS Safety Dashboard - Live Data Fetcher
Fetches real-time data from Motive API and KPA EHS API.
Saves JSON to data/ folder for the Streamlit dashboard.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")

MOTIVE_API_KEY = os.getenv("MOTIVE_API_KEY")
KPA_API_TOKEN = os.getenv("KPA_API_TOKEN")

MOTIVE_BASE = "https://api.gomotive.com"
KPA_BASE = "https://api.kpaehs.com/v1"

DATA_DIR = Path(__file__).parent / "data"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("fetch_live_data")


# ── Motive ────────────────────────────────────────────────────────────

def fetch_motive_events():
    """Fetch driver safety / speeding events from Motive (last 7 days)."""
    if not MOTIVE_API_KEY:
        log.error("MOTIVE_API_KEY not set — check .env file")
        return _empty_motive("No API key configured")

    headers = {"X-API-Key": MOTIVE_API_KEY}
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=7)
    all_events = []

    # Try v2 driver_performance_events (documented endpoint)
    try:
        log.info("Motive: trying GET /v2/driver_performance_events …")
        resp = requests.get(
            f"{MOTIVE_BASE}/v2/driver_performance_events",
            headers=headers,
            params={
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": end.strftime("%Y-%m-%d"),
                "per_page": 100,
                "page_no": 1,
            },
            timeout=15,
        )
        log.info(f"  → {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            events = data.get("driver_performance_events", [])
            all_events.extend(events)
            log.info(f"  ✓ {len(events)} events from v2")
        else:
            log.warning(f"  v2 failed: {resp.text[:300]}")
    except Exception as e:
        log.error(f"  v2 error: {e}")

    # Fallback: v1 safety/events
    if not all_events:
        try:
            log.info("Motive: trying GET /v1/safety/events …")
            resp = requests.get(
                f"{MOTIVE_BASE}/v1/safety/events",
                headers=headers,
                params={
                    "types": "speeding",
                    "start_time": start.isoformat(),
                    "end_time": end.isoformat(),
                },
                timeout=15,
            )
            log.info(f"  → {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                events = data.get("data", data.get("safety_events", []))
                if isinstance(events, list):
                    all_events.extend(events)
                log.info(f"  ✓ {len(all_events)} events from v1")
            else:
                log.warning(f"  v1 failed: {resp.text[:300]}")
        except Exception as e:
            log.error(f"  v1 error: {e}")

    return {
        "events": all_events,
        "count": len(all_events),
        "fetched_at": datetime.now().isoformat(),
        "period": {"start": start.isoformat(), "end": end.isoformat()},
    }


def _empty_motive(reason):
    now = datetime.now(timezone.utc)
    return {
        "events": [],
        "count": 0,
        "fetched_at": datetime.now().isoformat(),
        "period": {
            "start": (now - timedelta(days=7)).isoformat(),
            "end": now.isoformat(),
        },
        "error": reason,
    }


# ── KPA EHS helpers ───────────────────────────────────────────────────

def _kpa_post(method, payload=None):
    """POST to a KPA EHS API method (token goes in JSON body)."""
    body = dict(payload or {})
    body["token"] = KPA_API_TOKEN
    url = f"{KPA_BASE}/{method}"
    resp = requests.post(url, json=body, timeout=15)
    log.info(f"  KPA {method}: {resp.status_code}")
    if resp.status_code == 200:
        return resp.json()
    log.warning(f"  KPA {method} body: {resp.text[:300]}")
    return None


def _kpa_discover_forms():
    """Return list of forms from KPA, or empty list on failure."""
    try:
        data = _kpa_post("forms.list")
        if data and data.get("ok"):
            forms = data.get("forms", [])
            log.info(f"  KPA: discovered {len(forms)} forms")
            return forms
    except Exception as e:
        log.error(f"  KPA forms.list error: {e}")
    return []


def _kpa_fetch_responses(form_id, form_name, after_ms):
    """Fetch responses for a single KPA form."""
    try:
        data = _kpa_post("responses.list", {
            "form_id": form_id,
            "after": after_ms,
            "limit": 500,
        })
        if data and data.get("ok"):
            responses = data.get("responses", [])
            log.info(f"    form '{form_name}' → {len(responses)} responses")
            return responses
    except Exception as e:
        log.error(f"    form '{form_name}' error: {e}")
    return []


def _kpa_bearer_fallback(endpoint, label):
    """Last-resort GET with Bearer auth (may work on some KPA setups)."""
    try:
        log.info(f"  KPA: trying GET /{endpoint} with Bearer token …")
        resp = requests.get(
            f"{KPA_BASE}/{endpoint}",
            headers={
                "Authorization": f"Bearer {KPA_API_TOKEN}",
                "Content-Type": "application/json",
            },
            params={"days": 7},
            timeout=15,
        )
        log.info(f"    → {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            return data.get(label, data.get("responses", []))
    except Exception as e:
        log.error(f"    Bearer fallback error: {e}")
    return []


# ── KPA incidents ─────────────────────────────────────────────────────

INCIDENT_KEYWORDS = ["incident", "injury", "accident", "report"]

def fetch_kpa_incidents():
    """Fetch incidents from KPA EHS (last 7 days)."""
    if not KPA_API_TOKEN:
        log.error("KPA_API_TOKEN not set — check .env file")
        return _empty_kpa("incidents", "No API token configured")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    after_ms = int(start.timestamp() * 1000)
    all_items = []

    log.info("KPA Incidents: discovering forms …")
    forms = _kpa_discover_forms()
    for form in forms:
        name = (form.get("name") or "").lower()
        if any(kw in name for kw in INCIDENT_KEYWORDS):
            items = _kpa_fetch_responses(form["id"], form.get("name", ""), after_ms)
            all_items.extend(items)

    if not all_items:
        all_items = _kpa_bearer_fallback("incidents", "incidents")

    return {
        "incidents": all_items,
        "count": len(all_items),
        "fetched_at": datetime.now().isoformat(),
        "period": {"start": start.isoformat(), "end": now.isoformat()},
    }


# ── KPA observations ─────────────────────────────────────────────────

OBSERVATION_KEYWORDS = ["observation", "safety", "hazard", "near miss", "behavior"]

def fetch_kpa_observations():
    """Fetch observations from KPA EHS (last 7 days)."""
    if not KPA_API_TOKEN:
        log.error("KPA_API_TOKEN not set — check .env file")
        return _empty_kpa("observations", "No API token configured")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=7)
    after_ms = int(start.timestamp() * 1000)
    all_items = []

    log.info("KPA Observations: discovering forms …")
    forms = _kpa_discover_forms()
    for form in forms:
        name = (form.get("name") or "").lower()
        if any(kw in name for kw in OBSERVATION_KEYWORDS):
            items = _kpa_fetch_responses(form["id"], form.get("name", ""), after_ms)
            all_items.extend(items)

    if not all_items:
        all_items = _kpa_bearer_fallback("observations", "observations")

    return {
        "observations": all_items,
        "count": len(all_items),
        "fetched_at": datetime.now().isoformat(),
        "period": {"start": start.isoformat(), "end": now.isoformat()},
    }


def _empty_kpa(label, reason):
    now = datetime.now(timezone.utc)
    return {
        label: [],
        "count": 0,
        "fetched_at": datetime.now().isoformat(),
        "period": {
            "start": (now - timedelta(days=7)).isoformat(),
            "end": now.isoformat(),
        },
        "error": reason,
    }


# ── Save & main ───────────────────────────────────────────────────────

def save_json(filename, data):
    path = DATA_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    log.info(f"Saved {path.name}  ({path.stat().st_size:,} bytes)")


def main():
    bar = "=" * 60
    log.info(bar)
    log.info("BRHAS SAFETY DASHBOARD — LIVE DATA FETCH")
    log.info(bar)

    DATA_DIR.mkdir(exist_ok=True)

    motive = fetch_motive_events()
    incidents = fetch_kpa_incidents()
    observations = fetch_kpa_observations()

    save_json("motive_events.json", motive)
    save_json("kpa_incidents.json", incidents)
    save_json("kpa_observations.json", observations)

    log.info(bar)
    log.info(f"Motive events:     {motive['count']}")
    log.info(f"KPA incidents:     {incidents['count']}")
    log.info(f"KPA observations:  {observations['count']}")
    log.info("DONE")
    log.info(bar)


if __name__ == "__main__":
    main()
