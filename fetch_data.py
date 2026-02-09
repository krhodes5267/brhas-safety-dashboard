#!/usr/bin/env python3
"""
BRHAS Safety Dashboard - Data Fetching Script
Fetches data from Motive API and KPA EHS API
Runs daily via GitHub Actions at 6:30 AM
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# API Credentials (from environment variables)
MOTIVE_API_KEY = os.getenv("MOTIVE_API_KEY", "8d3dd502-36c0-47c4-ade3-a1fbbef0c05c")
KPA_API_TOKEN = os.getenv("KPA_API_TOKEN", "ppd4tH128Jsx3SwUJEjSsBqp0HNEXCxc6")

# API Endpoints
MOTIVE_BASE_URL = "https://api.gomotive.com/v1"
KPA_BASE_URL = "https://api.kpaehs.com/v1"

def log(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

def fetch_motive_events():
    """Fetch speeding events from Motive (last 7 days)"""
    log(">>> Fetching Motive speeding events...")
    
    headers = {
        "X-Api-Key": MOTIVE_API_KEY,
        "Content-Type": "application/json"
    }
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    try:
        url = f"{MOTIVE_BASE_URL}/safety/events"
        params = {
            "types": "speeding",
            "start_time": start_date.isoformat(),
            "end_time": end_date.isoformat()
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            events_count = len(data.get("data", []))
            log(f"✓ Motive: Fetched {events_count} speeding events")
            return data
        else:
            log(f"✗ Motive Error: {response.status_code}")
            return {"data": []}
    except Exception as e:
        log(f"✗ Motive Connection Error: {e}")
        return {"data": []}

def fetch_kpa_incidents():
    """Fetch incidents from KPA EHS (last 7 days)"""
    log(">>> Fetching KPA incidents...")
    
    headers = {
        "Authorization": f"Bearer {KPA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{KPA_BASE_URL}/incidents"
        params = {"days": 7}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            incidents_count = len(data.get("incidents", []))
            log(f"✓ KPA: Fetched {incidents_count} incidents")
            return data
        else:
            log(f"✗ KPA Error: {response.status_code}")
            return {"incidents": []}
    except Exception as e:
        log(f"✗ KPA Connection Error: {e}")
        return {"incidents": []}

def fetch_kpa_observations():
    """Fetch observations from KPA EHS (last 7 days)"""
    log(">>> Fetching KPA observations...")
    
    headers = {
        "Authorization": f"Bearer {KPA_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        url = f"{KPA_BASE_URL}/observations"
        params = {"days": 7}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            obs_count = len(data.get("observations", []))
            log(f"✓ KPA: Fetched {obs_count} observations")
            return data
        else:
            log(f"✗ KPA Error: {response.status_code}")
            return {"observations": []}
    except Exception as e:
        log(f"✗ KPA Connection Error: {e}")
        return {"observations": []}

def main():
    """Main execution"""
    log("=" * 70)
    log("BRHAS SAFETY DASHBOARD - DATA REFRESH")
    log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 70)
    
    # Create data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    log(f"\nData directory: {data_dir}")
    
    # Fetch data
    motive_data = fetch_motive_events()
    kpa_incidents = fetch_kpa_incidents()
    kpa_observations = fetch_kpa_observations()
    
    # Save data
    try:
        with open(data_dir / "motive_events.json", "w") as f:
            json.dump(motive_data, f, indent=2)
        log(f"✓ Saved: motive_events.json")
    except Exception as e:
        log(f"✗ Error saving motive data: {e}")
    
    try:
        with open(data_dir / "kpa_incidents.json", "w") as f:
            json.dump(kpa_incidents, f, indent=2)
        log(f"✓ Saved: kpa_incidents.json")
    except Exception as e:
        log(f"✗ Error saving incidents: {e}")
    
    try:
        with open(data_dir / "kpa_observations.json", "w") as f:
            json.dump(kpa_observations, f, indent=2)
        log(f"✓ Saved: kpa_observations.json")
    except Exception as e:
        log(f"✗ Error saving observations: {e}")
    
    log("\n" + "=" * 70)
    log("✓ DATA REFRESH COMPLETE")
    log("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
