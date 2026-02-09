#!/usr/bin/env python3
"""
BRHAS Safety Dashboard - Complete Automation Setup
Handles all phases: setup, API integration, dashboard generation, automation
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

class BRHASDashboardSetup:
    def __init__(self):
        self.base_dir = Path.home() / "Downloads" / "BRHAS-Dashboard"
        self.motive_api_key = "8d3dd502-36c0-47c4-ade3-a1fbbef0c05c"
        self.kpa_token = "ppd4tH128Jsx3SwUJEjSsBqp0HNEXCxc6"
        self.log_file = self.base_dir / "setup.log"
        
    def log(self, message):
        """Log messages to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        if self.base_dir.exists():
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
    
    def phase1_setup(self):
        """Phase 1: Setup & Configuration"""
        self.log("=" * 70)
        self.log("PHASE 1: SETUP & CONFIGURATION")
        self.log("=" * 70)
        
        # Create directory structure
        directories = [
            self.base_dir,
            self.base_dir / "data",
            self.base_dir / "logs",
            self.base_dir / "backups",
        ]
        
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.log(f"[OK] Created: {dir_path}")
        
        # Create credentials file (SECURE)
        creds_file = self.base_dir / "credentials.json"
        credentials = {
            "motive_api_key": self.motive_api_key,
            "kpa_token": self.kpa_token,
            "created": datetime.now().isoformat(),
            "note": "KEEP THIS FILE PRIVATE - contains API credentials"
        }
        
        with open(creds_file, "w") as f:
            json.dump(credentials, f, indent=2)
        
        # Set file permissions to read-only for owner
        os.chmod(creds_file, 0o600)
        self.log(f"[OK] Created secure credentials file: {creds_file}")
        
        return True
    
    def phase2_data_integration(self):
        """Phase 2: Fetch data from APIs"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 2: DATA INTEGRATION")
        self.log("=" * 70)
        
        # Fetch Motive data
        self.log("\n>>> Fetching Motive telematics data...")
        try:
            headers = {"X-Api-Key": self.motive_api_key}
            response = requests.get(
                "https://api.gomotive.com/v1/safety/events?types=speeding&days=7",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                motive_data = response.json()
                events_count = len(motive_data.get("data", []))
                self.log(f"[OK] Motive: Successfully fetched {events_count} speeding events")
                
                # Save data
                data_file = self.base_dir / "data" / "motive_events.json"
                with open(data_file, "w") as f:
                    json.dump(motive_data, f, indent=2)
                self.log(f"[OK] Saved to: {data_file}")
            else:
                self.log(f"[WARN] Motive API returned status {response.status_code}")
        except Exception as e:
            self.log(f"[FAIL] Motive Error: {e}")
        
        # Fetch KPA incidents
        self.log("\n>>> Fetching KPA incidents...")
        try:
            headers = {"Authorization": f"Bearer {self.kpa_token}"}
            response = requests.get(
                "https://api.kpaehs.com/v1/incidents?days=7",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                kpa_data = response.json()
                incidents_count = len(kpa_data.get("incidents", []))
                self.log(f"[OK] KPA: Successfully fetched {incidents_count} incidents")
                
                data_file = self.base_dir / "data" / "kpa_incidents.json"
                with open(data_file, "w") as f:
                    json.dump(kpa_data, f, indent=2)
                self.log(f"[OK] Saved to: {data_file}")
            else:
                self.log(f"[WARN] KPA API returned status {response.status_code}")
        except Exception as e:
            self.log(f"[FAIL] KPA Error: {e}")
        
        # Fetch KPA observations
        self.log("\n>>> Fetching KPA observations...")
        try:
            headers = {"Authorization": f"Bearer {self.kpa_token}"}
            response = requests.get(
                "https://api.kpaehs.com/v1/observations?days=7",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                kpa_obs = response.json()
                obs_count = len(kpa_obs.get("observations", []))
                self.log(f"[OK] KPA: Successfully fetched {obs_count} observations")
                
                data_file = self.base_dir / "data" / "kpa_observations.json"
                with open(data_file, "w") as f:
                    json.dump(kpa_obs, f, indent=2)
                self.log(f"[OK] Saved to: {data_file}")
            else:
                self.log(f"[WARN] KPA API returned status {response.status_code}")
        except Exception as e:
            self.log(f"[FAIL] KPA Error: {e}")
        
        return True
    
    def phase3_dashboard_generation(self):
        """Phase 3: Generate dashboard with live data"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 3: DASHBOARD GENERATION")
        self.log("=" * 70)
        
        # Copy dashboard HTML
        dashboard_src = Path(__file__).parent / "BRHAS-DASHBOARD-WHITE.html"
        dashboard_dst = self.base_dir / "dashboard.html"
        
        if dashboard_src.exists():
            with open(dashboard_src, "r") as f:
                dashboard_content = f.read()
            
            with open(dashboard_dst, "w") as f:
                f.write(dashboard_content)
            
            self.log(f"[OK] Dashboard copied to: {dashboard_dst}")
        else:
            self.log(f"[WARN] Dashboard template not found at {dashboard_src}")
        
        # Check for logo
        logo_path = self.base_dir / "butchs-logo.jpg"
        if logo_path.exists():
            self.log(f"[OK] Logo found: {logo_path}")
        else:
            self.log(f"[WARN] Logo not found. Place butchs-logo.jpg in {self.base_dir}")
        
        return True
    
    def phase4_automation(self):
        """Phase 4: Setup automation scripts"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 4: AUTOMATION SETUP")
        self.log("=" * 70)
        
        # Create daily refresh script
        refresh_script = self.base_dir / "update_dashboard.py"
        refresh_code = '''#!/usr/bin/env python3
import json
import requests
from datetime import datetime
from pathlib import Path

motive_key = "{}"
kpa_token = "{}"
base_dir = Path(__file__).parent

def refresh_data():
    print(f"[{{datetime.now().strftime('%H:%M:%S')}}] Starting refresh...")
    
    # Fetch Motive data
    try:
        response = requests.get(
            "https://api.gomotive.com/v1/safety/events?types=speeding&days=7",
            headers={{"X-Api-Key": motive_key}},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            with open(base_dir / "data" / "motive_events.json", "w") as f:
                json.dump(data, f)
            print(f"[OK] Motive: {{len(data.get('data', []))}} events")
    except Exception as e:
        print(f"[FAIL] Motive Error: {{e}}")
    
    # Fetch KPA data
    try:
        response = requests.get(
            "https://api.kpaehs.com/v1/incidents?days=7",
            headers={{"Authorization": f"Bearer {{kpa_token}}"}},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            with open(base_dir / "data" / "kpa_incidents.json", "w") as f:
                json.dump(data, f)
            print(f"[OK] KPA: {{len(data.get('incidents', []))}} incidents")
    except Exception as e:
        print(f"[FAIL] KPA Error: {{e}}")
    
    print(f"[{{datetime.now().strftime('%H:%M:%S')}}] Refresh complete!")

if __name__ == "__main__":
    refresh_data()
'''.format(self.motive_api_key, self.kpa_token)
        
        with open(refresh_script, "w") as f:
            f.write(refresh_code)
        
        os.chmod(refresh_script, 0o755)
        self.log(f"[OK] Created refresh script: {refresh_script}")
        
        # Create Windows batch file for Task Scheduler
        batch_file = self.base_dir / "run_refresh.bat"
        batch_content = f'''@echo off
cd {self.base_dir}
python update_dashboard.py
'''
        
        with open(batch_file, "w") as f:
            f.write(batch_content)
        
        self.log(f"[OK] Created batch file: {batch_file}")
        self.log(f"\n>>> To schedule daily refresh at 6:30 AM:")
        self.log(f"    1. Open Windows Task Scheduler (taskschd.msc)")
        self.log(f"    2. Create Basic Task")
        self.log(f"    3. Trigger: Daily at 6:30 AM")
        self.log(f"    4. Action: Start program")
        self.log(f"    5. Program: {batch_file}")
        
        return True
    
    def phase5_deployment(self):
        """Phase 5: Deployment setup"""
        self.log("\n" + "=" * 70)
        self.log("PHASE 5: DEPLOYMENT")
        self.log("=" * 70)
        
        onedrive_path = Path.home() / "OneDrive" / "BRHAS-Dashboard"
        self.log(f"\n>>> OneDrive deployment path:")
        self.log(f"    {onedrive_path}")
        self.log(f"\n    To deploy:")
        self.log(f"    1. Create folder: {onedrive_path}")
        self.log(f"    2. Copy dashboard.html")
        self.log(f"    3. Copy butchs-logo.jpg")
        self.log(f"    4. Right-click folder > Share")
        self.log(f"    5. Add: Sam Ares, Kelly Rhodes, field supervisors")
        
        return True
    
    def run_all(self):
        """Run all phases"""
        self.log("BRHAS SAFETY DASHBOARD - COMPLETE AUTOMATION")
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            self.phase1_setup()
            self.phase2_data_integration()
            self.phase3_dashboard_generation()
            self.phase4_automation()
            self.phase5_deployment()
            
            self.log("\n" + "=" * 70)
            self.log("[OK] ALL PHASES COMPLETE!")
            self.log("=" * 70)
            self.log("\nNext steps:")
            self.log("1. Verify API credentials are working")
            self.log("2. Check data files in data/ folder")
            self.log("3. Open dashboard.html in browser")
            self.log("4. Set up Windows Task Scheduler")
            self.log("5. Deploy to OneDrive")
            self.log(f"\nSetup log saved to: {self.log_file}")
            
            return True
        except Exception as e:
            self.log(f"\n[FAIL] ERROR: {e}")
            return False

if __name__ == "__main__":
    setup = BRHASDashboardSetup()
    success = setup.run_all()
    sys.exit(0 if success else 1)
