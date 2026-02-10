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

LOOKBACK_DAYS = 90  # Fetch 90 days so dashboard 7/30/90/custom filters all work


def fetch_motive_events():
    """Fetch driver safety events from Motive (last 90 days, paginated)."""
    if not MOTIVE_API_KEY:
        log.error("MOTIVE_API_KEY not set — check .env file")
        return _empty_motive("No API key configured")

    headers = {"X-API-Key": MOTIVE_API_KEY}
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=LOOKBACK_DAYS)
    all_events = []

    # Try v2 driver_performance_events with pagination
    try:
        page = 1
        while True:
            log.info(f"Motive: GET /v2/driver_performance_events page {page} …")
            resp = requests.get(
                f"{MOTIVE_BASE}/v2/driver_performance_events",
                headers=headers,
                params={
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d"),
                    "per_page": 100,
                    "page_no": page,
                },
                timeout=30,
            )
            log.info(f"  → {resp.status_code}")
            if resp.status_code != 200:
                log.warning(f"  v2 failed: {resp.text[:300]}")
                break
            data = resp.json()
            events = data.get("driver_performance_events", [])
            if not events:
                break
            all_events.extend(events)
            log.info(f"  ✓ page {page}: {len(events)} events (total: {len(all_events)})")
            # Stop if fewer than a full page (last page)
            if len(events) < 100:
                break
            page += 1
            if page > 50:  # safety cap
                break
    except Exception as e:
        log.error(f"  v2 error: {e}")

    # Fallback: v1 safety/events (no pagination)
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
                timeout=30,
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
            "start": (now - timedelta(days=LOOKBACK_DAYS)).isoformat(),
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
    resp = requests.post(url, json=body, timeout=30)
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


def _kpa_fetch_flat(form_id, form_name, after_ms):
    """Fetch responses via responses.flat (JSON) — gives labeled fields.

    Paginates using 'after' timestamp to get all records (max 1000/page).
    Returns a list of dicts, each with human-readable keys like
    'Service Line', 'District', 'report number', etc.
    """
    all_results = []
    cursor = after_ms
    header = None
    page = 0

    try:
        while True:
            page += 1
            data = _kpa_post("responses.flat", {
                "form_id": form_id,
                "after": cursor,
                "limit": 1000,
                "format": "json",
            })
            if not data or not data.get("ok"):
                break

            rows = data.get("responses", [])
            if len(rows) < 2:
                break

            # First row is always the header
            if header is None:
                header = rows[0]
            data_rows = rows[1:]

            for row in data_rows:
                record = {}
                for field_id, value in row.items():
                    col_name = header.get(field_id, field_id)
                    record[col_name] = value
                all_results.append(record)

            # If we got a full page, advance cursor to latest Updated Time
            if len(data_rows) >= 1000:
                # Find the max updated timestamp to use as next cursor
                max_ts = cursor
                for row in data_rows:
                    ut = row.get("updated_time") or row.get("Updated Time")
                    if ut and isinstance(ut, (int, float)) and ut > max_ts:
                        max_ts = int(ut)
                if max_ts > cursor:
                    cursor = max_ts
                else:
                    break  # can't advance, stop
            else:
                break  # last page

            if page >= 20:  # safety cap
                break

        if all_results:
            log.info(f"    form '{form_name}' → {len(all_results)} rows "
                     f"({page} page{'s' if page > 1 else ''})")
        return all_results
    except Exception as e:
        log.error(f"    form '{form_name}' flat error: {e}")
    return []


# ── KPA incidents ─────────────────────────────────────────────────────

INCIDENT_KEYWORDS = ["incident", "injury", "accident", "report"]

def fetch_kpa_incidents():
    """Fetch incidents from KPA EHS (last 90 days) with full field data."""
    if not KPA_API_TOKEN:
        log.error("KPA_API_TOKEN not set — check .env file")
        return _empty_kpa("incidents", "No API token configured")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=LOOKBACK_DAYS)
    after_ms = int(start.timestamp() * 1000)
    all_items = []

    log.info("KPA Incidents: discovering forms …")
    forms = _kpa_discover_forms()
    for form in forms:
        name = (form.get("name") or "").lower()
        if any(kw in name for kw in INCIDENT_KEYWORDS):
            items = _kpa_fetch_flat(form["id"], form.get("name", ""), after_ms)
            all_items.extend(items)

    return {
        "incidents": all_items,
        "count": len(all_items),
        "fetched_at": datetime.now().isoformat(),
        "period": {"start": start.isoformat(), "end": now.isoformat()},
    }


# ── KPA observations ─────────────────────────────────────────────────

OBSERVATION_KEYWORDS = ["observation", "safety", "hazard", "near miss", "behavior"]

def fetch_kpa_observations():
    """Fetch observations from KPA EHS (last 90 days) with full field data."""
    if not KPA_API_TOKEN:
        log.error("KPA_API_TOKEN not set — check .env file")
        return _empty_kpa("observations", "No API token configured")

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=LOOKBACK_DAYS)
    after_ms = int(start.timestamp() * 1000)
    all_items = []

    log.info("KPA Observations: discovering forms …")
    forms = _kpa_discover_forms()
    for form in forms:
        name = (form.get("name") or "").lower()
        if any(kw in name for kw in OBSERVATION_KEYWORDS):
            items = _kpa_fetch_flat(form["id"], form.get("name", ""), after_ms)
            all_items.extend(items)

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
            "start": (now - timedelta(days=LOOKBACK_DAYS)).isoformat(),
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
