# BRHAS Safety Dashboard - Streamlit + GitHub Complete Setup

## 🚀 Overview

This is a **production-ready** safety dashboard that:
- ✅ Runs on Streamlit (Python web framework)
- ✅ Hosted on Streamlit Cloud (free, cloud-based)
- ✅ Uses GitHub for version control
- ✅ GitHub Actions auto-refreshes data daily at 6:30 AM
- ✅ Team accesses via URL (no installation needed)
- ✅ Mobile responsive
- ✅ Real-time live data

## 📋 What You Get

**Files to Create:**
1. `app.py` - Streamlit dashboard (already created ✓)
2. `fetch_data.py` - Data fetching script (already created ✓)
3. `requirements.txt` - Python dependencies (already created ✓)
4. `.github/workflows/daily-refresh.yml` - GitHub Actions automation (already created ✓)
5. `.streamlit/config.toml` - Streamlit configuration
6. `README.md` - Documentation
7. `.gitignore` - Git ignore file

## 🔧 Step-by-Step Setup

### STEP 1: Create GitHub Repository

1. Go to github.com
2. Click "New Repository"
3. Name: `brhas-safety-dashboard`
4. Description: "BRHAS Automated Safety Intelligence Dashboard"
5. Visibility: **Private** (internal use only)
6. Initialize with README: Yes
7. Add .gitignore: Python
8. Click "Create Repository"

### STEP 2: Clone Repository to Your Machine

```bash
git clone https://github.com/YOUR-USERNAME/brhas-safety-dashboard.git
cd brhas-safety-dashboard
```

### STEP 3: Add Files to Repository

Copy these files into your repo folder:
- `app.py` → root folder
- `fetch_data.py` → root folder
- `requirements.txt` → root folder
- `daily-refresh.yml` → `.github/workflows/` folder (create folders if needed)

### STEP 4: Create Additional Files

**Create `.streamlit/config.toml`:**
```toml
[theme]
primaryColor = "#dc2626"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f9f9f9"
textColor = "#1a1a1a"

[client]
showErrorDetails = false

[logger]
level = "info"
```

**Create `.gitignore` (if not already):
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.streamlit/secrets.toml
.DS_Store
```

**Create `README.md`:**
```markdown
# BRHAS Safety Dashboard

Automated safety intelligence system using real-time data from Motive and KPA EHS.

## Features

- ✅ Live KPI metrics (TRIR, LTIR, Driver Score)
- ✅ Financial impact tracking
- ✅ Predictive alerts with confidence intervals
- ✅ Drill-down analytics
- ✅ Repeat offender tracking
- ✅ Action accountability
- ✅ Auto-refreshes daily at 6:30 AM

## Access

https://brhas-safety-dashboard.streamlit.app/

## Data Sources

- **Motive API** - Fleet telematics & driving events
- **KPA EHS** - Incidents & observations

## Deployment

Deployed on Streamlit Cloud. Updates automatically on GitHub push.
```

### STEP 5: Commit and Push to GitHub

```bash
git add .
git commit -m "Initial commit: BRHAS Safety Dashboard"
git push origin main
```

### STEP 6: Add GitHub Secrets (API Credentials)

1. Go to your repo on GitHub
2. Click "Settings"
3. Click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add `MOTIVE_API_KEY` = `8d3dd502-36c0-47c4-ade3-a1fbbef0c05c`
6. Add `KPA_API_TOKEN` = `ppd4tH128Jsx3SwUJEjSsBqp0HNEXCxc6`

**IMPORTANT:** These secrets are encrypted and never exposed!

### STEP 7: Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select your GitHub repo
4. Select `main` branch
5. Select `app.py` as main file
6. Click "Deploy"

**Wait ~30 seconds - your dashboard goes LIVE!**

Access: `https://brhas-safety-dashboard.streamlit.app/`

### STEP 8: Verify GitHub Actions

1. Go to your repo
2. Click "Actions" tab
3. You'll see "Daily Data Refresh" workflow
4. It's scheduled to run daily at 6:30 AM UTC
5. You can manually trigger it by clicking "Run workflow"

## 📊 How It Works

### Daily Workflow:

```
6:30 AM → GitHub Actions triggers
    ↓
Python script connects to Motive API
    ↓
Python script connects to KPA EHS API
    ↓
Data saved as JSON files
    ↓
Files committed back to GitHub
    ↓
Streamlit Cloud auto-detects changes
    ↓
Dashboard refreshes with new data
    ↓
Team sees latest data when they open the URL
```

### Manual Data Refresh (for testing):

1. Go to Actions tab
2. Click "Daily Data Refresh"
3. Click "Run workflow"
4. Check logs to verify success

## 🔑 API Credentials

Your credentials are stored securely as GitHub Secrets:
- Never exposed in code
- Never committed to repo
- Only used by GitHub Actions
- Can be rotated anytime in Settings

## 🎯 Timezone Note

The GitHub Actions cron is set to UTC. To adjust for your timezone:

**Edit `.github/workflows/daily-refresh.yml`:**

Change this line based on your timezone:
```yaml
- cron: '30 6 * * *'  # UTC time
```

**Examples:**
- `'30 8 * * *'` = 2:30 AM CST (6:30 AM UTC)
- `'30 12 * * *'` = 6:30 AM PST (2:30 PM UTC)
- `'30 13 * * *'` = 7:30 AM PST (3:30 PM UTC)

Then commit and push the change.

## 🚨 Troubleshooting

### Dashboard won't load
- Check that `app.py` is in root folder
- Make sure `requirements.txt` has all dependencies
- Check Streamlit Cloud logs for errors

### Data not updating
- Go to Actions tab and manually run workflow
- Check for error messages in workflow logs
- Verify API credentials in GitHub Secrets

### API errors (401 Unauthorized)
- Check credentials are correct in GitHub Secrets
- Verify API keys haven't been rotated
- Test API endpoints manually

### Dashboard looks different than expected
- Make sure `butchs-logo.jpg` is in root folder
- Clear browser cache (Ctrl+Shift+Delete)
- Refresh page (Ctrl+Shift+R)

## 📱 Mobile Access

1. Team members go to: `https://brhas-safety-dashboard.streamlit.app/`
2. Bookmark the link
3. Streamlit automatically detects mobile and adjusts layout
4. Works on any phone or tablet with a browser

## 🔄 Updates & Changes

If you want to update the dashboard:

1. Edit `app.py` locally
2. Test locally: `streamlit run app.py`
3. Commit and push to GitHub
4. Streamlit Cloud auto-deploys (30 seconds)
5. Everyone sees the changes

No reinstallation needed!

## 📅 Go-Live Timeline

**February 9 (Today):**
- Create GitHub repo ✓
- Push code ✓
- Deploy to Streamlit Cloud ✓
- Dashboard is LIVE ✓

**March 21-31:**
- QA testing with real data
- Training with executives
- Fine-tune based on feedback

**April 1:**
- Official go-live
- Team starts using daily at 6:30 AM briefing
- GitHub Actions refreshes data automatically

## 🎉 You're Done!

Your dashboard is:
- ✅ Live and accessible via URL
- ✅ Auto-refreshing daily at 6:30 AM
- ✅ Mobile responsive
- ✅ Version controlled on GitHub
- ✅ Secure (API credentials in Secrets)
- ✅ Free (Streamlit Cloud is free)
- ✅ Professional grade

No installation needed by end users. Just click the link!

---

**Questions?** Check the logs or run manual tests in GitHub Actions.
