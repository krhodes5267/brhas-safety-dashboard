import re
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import Counter
import calendar

# ── Page config ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="BRHAS Safety Dashboard",
    page_icon="🏭",
    layout="wide",
)

DATA_DIR = Path(__file__).parent / "data"
LOGO_PATH = Path(__file__).parent / "butchs-logo.jpg"

# ── Brand colors ──────────────────────────────────────────────────────

RED = "#dc2626"
DARK = "#1e293b"
GREEN = "#059669"
BLUE = "#2563eb"
YELLOW = "#d97706"
GRAY = "#64748b"
DARK_GREEN = "#047857"

# ── Yard definitions ─────────────────────────────────────────────────

YARD_ORDER = ["Midland", "Bryan", "Kilgore", "Hobbs",
              "Jourdanton", "Levelland", "Barstow"]

YARD_REGIONS = {
    "Midland":    ["midland", "yukon", "odessa", "west odessa", "stanton",
                   "big spring", "garden city", "crane", "rankin", "mccamey"],
    "Bryan":      ["bryan", "college station", "palestine", "madisonville",
                   "hearne", "navasota", "huntsville"],
    "Kilgore":    ["kilgore", "tyler", "longview", "henderson", "marshall",
                   "jacksonville", "carthage", "lufkin", "nacogdoches"],
    "Hobbs":      ["hobbs", "seminole", "lovington", "carlsbad", "artesia",
                   "eunice", "jal", "tatum"],
    "Jourdanton": ["jourdanton", "pleasanton", "floresville", "poteet",
                   "kenedy", "karnes city", "falls city", "laredo",
                   "edinburg"],
    "Levelland":  ["levelland", "lubbock", "brownfield", "post", "lamesa",
                   "snyder", "tahoka", "slaton", "wolfforth", "littlefield"],
    "Barstow":    ["barstow", "pecos", "kermit", "monahans", "fort stockton",
                   "wink", "mentone", "toyah"],
}

DISTRICT_ALIASES = {"midland yukon": "Midland"}
CASING_SERVICE_LINES = {"casing"}

CSG_AUDIT_FORM = "CSG - Safety Casing Field Assessment"

# ── Custom CSS ────────────────────────────────────────────────────────

st.markdown("""
<style>
    .section-hdr {
        font-size: 20px; font-weight: 800; color: #dc2626;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 32px 0 12px 0; padding-bottom: 8px;
        border-bottom: 3px solid #dc2626;
    }
    .kpi-card {
        background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
        padding: 18px 14px; text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
                  color: #64748b; font-weight: 700; margin-bottom: 6px; }
    .kpi-value { font-size: 28px; font-weight: 900; margin-bottom: 4px; }
    .kpi-detail { font-size: 10px; color: #94a3b8; }
    .kpi-badge-red { display: inline-block; margin-top: 6px; background: #fee2e2;
                     color: #991b1b; padding: 2px 10px; border-radius: 4px;
                     font-size: 10px; font-weight: 700; }
    .kpi-badge-green { display: inline-block; margin-top: 6px; background: #d1fae5;
                       color: #065f46; padding: 2px 10px; border-radius: 4px;
                       font-size: 10px; font-weight: 700; }
    .kpi-badge-yellow { display: inline-block; margin-top: 6px; background: #fef3c7;
                        color: #92400e; padding: 2px 10px; border-radius: 4px;
                        font-size: 10px; font-weight: 700; }
    .alert-box {
        border-radius: 8px; padding: 16px 20px; margin-bottom: 12px;
    }
    .alert-critical {
        background: linear-gradient(135deg, #fef2f2, #fff5f5);
        border: 1px solid #fecaca; border-left: 5px solid #dc2626;
    }
    .alert-warning {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 1px solid #fde68a; border-left: 5px solid #d97706;
    }
    .alert-stable {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1px solid #bbf7d0; border-left: 5px solid #059669;
    }
    .alert-improving {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border: 1px solid #a7f3d0; border-left: 5px solid #047857;
    }
    .alert-title { font-size: 14px; font-weight: 800;
                    text-transform: uppercase; margin-bottom: 6px; }
    .alert-body  { font-size: 13px; color: #1e293b; line-height: 1.6; }
    .logo-box {
        width: 72px; height: 72px; border-radius: 12px;
        background: linear-gradient(135deg, #dc2626, #991b1b);
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-size: 32px; font-weight: 900;
        font-family: Georgia, serif; letter-spacing: -1px;
        box-shadow: 0 2px 8px rgba(220,38,38,0.3);
    }
    .yard-hdr {
        font-size: 15px; font-weight: 700; color: #1e293b;
        margin-bottom: 4px;
    }
    .footer-text { font-size: 11px; color: #94a3b8; text-align: center; }
    .manual-tag {
        display: inline-block; font-size: 9px; background: #f1f5f9;
        color: #64748b; padding: 1px 6px; border-radius: 3px;
        font-weight: 600; letter-spacing: 0.5px; margin-left: 6px;
        vertical-align: middle; text-transform: uppercase;
    }

    @media (prefers-color-scheme: dark) {
        .kpi-card { background: #1e293b !important; border-color: #334155 !important;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important; }
        .kpi-label { color: #94a3b8 !important; }
        .kpi-detail { color: #64748b !important; }
        .alert-critical, .alert-warning, .alert-stable, .alert-improving {
            background: linear-gradient(135deg, #1a1a2e, #2d1f1f) !important; }
        .alert-body { color: #e2e8f0 !important; }
        .yard-hdr { color: #e2e8f0 !important; }
        .footer-text { color: #64748b !important; }
        .manual-tag { background: #334155 !important; color: #94a3b8 !important; }
        .kpi-badge-red { background: #7f1d1d !important; color: #fecaca !important; }
        .kpi-badge-green { background: #064e3b !important; color: #a7f3d0 !important; }
        .kpi-badge-yellow { background: #78350f !important; color: #fde68a !important; }
    }
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14"] .kpi-card,
    [data-testid="stAppViewContainer"][style*="background-color: rgb(0"] .kpi-card {
        background: #1e293b !important; border-color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
#  HELPER FUNCTIONS
# =====================================================================

def is_casing_vehicle(vehicle_number):
    """Return True if the vehicle belongs to the Casing division."""
    if not vehicle_number:
        return False
    vn = vehicle_number.strip()
    if "-RAT-" in vn:
        return True
    if re.match(r"^\d+C(\s|$|-)", vn):
        return True
    return False


def location_to_yard(loc_str):
    """Map a Motive location string to the nearest casing yard."""
    if not loc_str:
        return None
    low = loc_str.lower()
    for yard, keywords in YARD_REGIONS.items():
        if any(kw in low for kw in keywords):
            return yard
    return None


def normalize_district(raw_district):
    """Combine Midland Yukon / Midland PER into Midland."""
    if not raw_district:
        return raw_district
    key = raw_district.strip().lower()
    return DISTRICT_ALIASES.get(key, raw_district.strip())


def parse_event_date(date_str):
    """Parse date from various formats. Returns date object or None."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
    except Exception:
        pass
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        pass
    return None


# =====================================================================
#  DATA LOADING
# =====================================================================

@st.cache_data(ttl=300)
def load_json(filename):
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


motive_raw = load_json("motive_events.json")
incidents_raw = load_json("kpa_incidents.json")
observations_raw = load_json("kpa_observations.json")

# Fetch timestamp
fetched_raw = ""
for raw in [motive_raw, incidents_raw, observations_raw]:
    if raw and raw.get("fetched_at"):
        fetched_raw = raw["fetched_at"]
        break
try:
    fetched_dt = datetime.fromisoformat(fetched_raw)
    fetched_str = fetched_dt.strftime("%b %d, %Y at %I:%M %p")
except Exception:
    fetched_str = fetched_raw or "---"


# =====================================================================
#  BUILD FLAT EVENT LISTS (filtered to Casing Division)
# =====================================================================

def get_all_motive_events():
    """Parse all Casing Division motive events into flat dicts."""
    if not motive_raw:
        return []
    events = []
    for entry in motive_raw.get("events", []):
        evt = entry.get("driver_performance_event", entry)
        veh = evt.get("vehicle") or {}
        if not is_casing_vehicle(veh.get("number", "")):
            continue
        drv = evt.get("driver") or {}
        driver_name = ""
        if drv.get("first_name"):
            driver_name = f"{drv['first_name']} {drv.get('last_name', '')}".strip()
        events.append({
            "id": evt.get("id", ""),
            "type": evt.get("type", "unknown"),
            "date": parse_event_date(evt.get("start_time", "")),
            "date_str": (evt.get("start_time") or "")[:10],
            "location": evt.get("location", ""),
            "yard": location_to_yard(evt.get("location", "")),
            "driver": driver_name,
            "vehicle": veh.get("number", ""),
            "start_speed": evt.get("start_speed"),
            "end_speed": evt.get("end_speed"),
        })
    return events


def get_all_kpa_items(raw, key):
    """Parse all Casing Division KPA items with normalized fields."""
    if not raw:
        return []
    items = []
    for item in raw.get(key, []):
        sl = (item.get("Service Line") or item.get("service_line") or "").strip().lower()
        if sl not in CASING_SERVICE_LINES:
            continue
        item["_date"] = parse_event_date(item.get("Date", ""))
        item["_district"] = normalize_district(item.get("District", ""))
        items.append(item)
    return items


def get_all_rig_audits(raw):
    """Extract CSG - Safety Casing Field Assessment records from observations.

    These have an empty Service Line so they're missed by the Casing filter.
    We identify them by the Report field and compute a checklist score from
    the Yes/OK vs No answers in the record.
    """
    if not raw:
        return []
    PASS_VALUES = {"Yes", "OK"}
    FAIL_VALUES = {"No"}
    SKIP_KEYS = {
        "Report", "Report Number", "Date", "District", "Observer",
        "Observer Emp#", "Rig", "Audit Type", "Link", "Service Line",
        "Updated", "Updated Time", "Version", "Latitude", "Longitude",
        "Temperature", "Wind Speed", "Weather", "Duration (Seconds)",
        "Parent Report Number", "Parent Link", "Surrogate", "Completed by",
        "Customer", "Name", "Number of Crew Members Involved",
        "Date Conducted", "Date Conducted Latitude",
        "Date Conducted Longitude", "1st Obs", "2nd Obs",
        "_date", "_district",
    }
    audits = []
    for item in raw.get("observations", []):
        if item.get("Report") != CSG_AUDIT_FORM:
            continue

        # Compute checklist score
        passed = 0
        failed = 0
        failed_items = []
        for k, v in item.items():
            if k in SKIP_KEYS or not isinstance(v, str):
                continue
            if v in PASS_VALUES:
                passed += 1
            elif v in FAIL_VALUES:
                failed += 1
                failed_items.append(k)

        total = passed + failed
        score = round(passed / total * 100) if total > 0 else 0

        item["_date"] = parse_event_date(item.get("Date", ""))
        item["_district"] = normalize_district(item.get("District", ""))
        item["_score"] = score
        item["_passed"] = passed
        item["_failed"] = failed
        item["_total_checked"] = total
        item["_failed_items"] = failed_items
        audits.append(item)
    return audits


# Pre-parse all data
all_motive = get_all_motive_events()
all_incidents = get_all_kpa_items(incidents_raw, "incidents")
all_observations = get_all_kpa_items(observations_raw, "observations")
all_audits = get_all_rig_audits(observations_raw)


# =====================================================================
#  PREDICTIVE ALERT CALCULATION (from real data)
# =====================================================================

def calculate_predictive_alerts(motive_events, kpa_incidents):
    """Calculate data-driven trend alerts for each yard."""
    today = date.today()
    current_month_start = today.replace(day=1)
    prev_month_end = current_month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_elapsed = today.day

    prev_month_name = prev_month_end.strftime("%b")
    current_month_name = today.strftime("%b")
    month_end_str = f"{current_month_name} {days_in_month}"

    alerts = {}
    for yard in YARD_ORDER:
        current_count = 0
        prev_count = 0

        for evt in motive_events:
            if evt.get("yard") != yard:
                continue
            d = evt.get("date")
            if not d:
                continue
            if current_month_start <= d <= today:
                current_count += 1
            elif prev_month_start <= d <= prev_month_end:
                prev_count += 1

        for item in kpa_incidents:
            if item.get("_district") != yard:
                continue
            d = item.get("_date")
            if not d:
                continue
            if current_month_start <= d <= today:
                current_count += 1
            elif prev_month_start <= d <= prev_month_end:
                prev_count += 1

        # Trend calculation
        if prev_count > 0:
            trend_pct = ((current_count - prev_count) / prev_count) * 100
        elif current_count > 0:
            trend_pct = 100.0
        else:
            trend_pct = 0.0

        # Projection
        daily_avg = current_count / max(days_elapsed, 1)
        projected = round(daily_avg * days_in_month)

        # Confidence based on how far into the month we are
        confidence = min(95, round((days_elapsed / days_in_month) * 100))

        # Color-coded alert levels
        if trend_pct >= 30:
            level, color, label = "critical", RED, "HIGH RISK"
        elif trend_pct >= 10:
            level, color, label = "warning", YELLOW, "WARNING"
        elif trend_pct >= -10:
            level, color, label = "stable", GREEN, "STABLE"
        else:
            level, color, label = "improving", DARK_GREEN, "IMPROVING"

        alerts[yard] = {
            "current": current_count, "previous": prev_count,
            "trend_pct": trend_pct, "daily_avg": daily_avg,
            "projected": projected, "confidence": confidence,
            "level": level, "color": color, "label": label,
            "prev_month": prev_month_name,
            "current_month": current_month_name,
            "month_end": month_end_str,
        }
    return alerts


# =====================================================================
#  SIDEBAR  ---  Interactive Controls
# =====================================================================

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=140)
    else:
        st.markdown(
            f'<div style="font-size:24px; font-weight:900; color:{RED};">BRHAS</div>',
            unsafe_allow_html=True)
    st.markdown(
        f'<span style="font-weight:700; color:{RED};">Casing Division</span>',
        unsafe_allow_html=True)
    st.caption(f"Updated: {fetched_str}")
    st.divider()

    st.markdown("### Dashboard Controls")

    # ── Time Period Selector ──
    time_period = st.selectbox(
        "Time Period",
        ["7 Days", "30 Days", "90 Days", "Custom Range"],
        index=0,
    )

    today = date.today()
    if time_period == "Custom Range":
        c_start, c_end = st.columns(2)
        with c_start:
            start_date = st.date_input("Start", today - timedelta(days=30))
        with c_end:
            end_date = st.date_input("End", today)
    elif time_period == "30 Days":
        start_date, end_date = today - timedelta(days=30), today
    elif time_period == "90 Days":
        start_date, end_date = today - timedelta(days=90), today
    else:
        start_date, end_date = today - timedelta(days=7), today

    st.divider()

    # ── Yard Selector ──
    selected_yard = st.selectbox("Yard", ["All Yards"] + YARD_ORDER, index=0)

    st.divider()

    # ── View Mode ──
    view_mode = st.radio(
        "View Mode",
        ["Division Overview", "Individual Yard", "Comparison"],
        index=0,
    )

    st.divider()


# =====================================================================
#  APPLY FILTERS
# =====================================================================

# Date filter — only include items with a parseable date inside the range
motive_filtered = [
    e for e in all_motive
    if e.get("date") is not None and start_date <= e["date"] <= end_date
]
incidents_filtered = [
    i for i in all_incidents
    if i.get("_date") is not None and start_date <= i["_date"] <= end_date
]
observations_filtered = [
    o for o in all_observations
    if o.get("_date") is not None and start_date <= o["_date"] <= end_date
]
audits_filtered = [
    a for a in all_audits
    if a.get("_date") is not None and start_date <= a["_date"] <= end_date
]

# Yard filter (applied to display lists)
if selected_yard == "All Yards":
    motive_display = motive_filtered
    incidents_display = incidents_filtered
    observations_display = observations_filtered
    audits_display = audits_filtered
else:
    motive_display = [e for e in motive_filtered if e.get("yard") == selected_yard]
    incidents_display = [i for i in incidents_filtered if i.get("_district") == selected_yard]
    observations_display = [o for o in observations_filtered if o.get("_district") == selected_yard]
    audits_display = [a for a in audits_filtered if a.get("_district") == selected_yard]

# Aggregated metrics
by_type = Counter(e["type"] for e in motive_display)
by_day = Counter(e["date_str"] for e in motive_display if e.get("date_str"))
by_yard = Counter(e["yard"] for e in motive_display if e.get("yard"))
drivers = Counter(e["driver"] for e in motive_display if e.get("driver"))
unique_drivers = len(drivers)

# Predictive alerts (always from full unfiltered data for month calc)
alerts = calculate_predictive_alerts(all_motive, all_incidents)


# ── Sidebar quick stats (after filtering) ──
with st.sidebar:
    st.markdown("**Filtered Stats**")
    qs1, qs2 = st.columns(2)
    qs1.metric("Events", len(motive_display))
    qs2.metric("Observations", len(observations_display))
    qs3, qs4 = st.columns(2)
    qs3.metric("Incidents", len(incidents_display))
    qs4.metric("Rig Audits", len(audits_display))


# =====================================================================
#  HEADER
# =====================================================================

col_logo, col_title = st.columns([0.12, 0.88])

with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=80)
    else:
        st.markdown('<div class="logo-box">B</div>', unsafe_allow_html=True)

with col_title:
    title_suffix = f" --- {selected_yard}" if selected_yard != "All Yards" else ""
    st.markdown(
        f'<span style="font-size:32px; font-weight:900; color:{RED};">'
        f'BRHAS Safety Dashboard{title_suffix}</span>',
        unsafe_allow_html=True)
    period_label = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    st.markdown(
        f'<span style="font-size:14px; color:{GRAY};">'
        f'Casing Division &nbsp;|&nbsp; {view_mode}'
        f' &nbsp;|&nbsp; {period_label}'
        f' &nbsp;|&nbsp; Updated: {fetched_str}</span>',
        unsafe_allow_html=True)

# Filter summary
parts = [f"Motive: **{len(motive_display)}** events",
         f"Incidents: **{len(incidents_display)}**",
         f"Observations: **{len(observations_display)}**"]
if selected_yard != "All Yards":
    parts.append(f"Yard: **{selected_yard}**")
st.caption("Casing Division --- " + " | ".join(parts))
st.divider()


# =====================================================================
#  VIEW: DIVISION OVERVIEW
# =====================================================================

if view_mode == "Division Overview":

    # ── 1  KPI Targets vs Actual ──
    st.markdown(
        '<div class="section-hdr">KPI Targets vs Actual</div>',
        unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">TRIR <span class="manual-tag">MANUAL</span></div>
            <div class="kpi-value" style="color:#dc2626">2.3</div>
            <div class="kpi-detail">Target: &lt;2.0 &nbsp;|&nbsp; Industry: 3.5</div>
            <div class="kpi-badge-red">ABOVE TARGET</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">LTIR <span class="manual-tag">MANUAL</span></div>
            <div class="kpi-value" style="color:#dc2626">0.8</div>
            <div class="kpi-detail">Target: &lt;0.5 &nbsp;|&nbsp; Industry: 1.2</div>
            <div class="kpi-badge-red">ABOVE TARGET</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">Driver Score <span class="manual-tag">MANUAL</span></div>
            <div class="kpi-value" style="color:#d97706">78</div>
            <div class="kpi-detail">Target: &gt;85 &nbsp;|&nbsp; Industry: 72</div>
            <div class="kpi-badge-red">BELOW TARGET</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        days_in_period = max((end_date - start_date).days, 1)
        obs_rate = len(observations_display) / days_in_period
        obs_target = max(1, round(30 * days_in_period / 7))
        obs_on_track = len(observations_display) >= obs_target
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Observations ({time_period})</div>
            <div class="kpi-value" style="color:{GREEN if obs_on_track else YELLOW}">{len(observations_display)}</div>
            <div class="kpi-detail">Target: {obs_target}+ &nbsp;|&nbsp; Rate: {obs_rate:.1f}/day</div>
            <div class="{'kpi-badge-green' if obs_on_track else 'kpi-badge-yellow'}">{'ON TRACK' if obs_on_track else 'BELOW TARGET'}</div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── 2  Financial Impact ──
    st.markdown(
        '<div class="section-hdr">Financial Impact'
        ' <span class="manual-tag">MANUAL ENTRY</span></div>',
        unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">Workers' Comp</div>
            <div class="kpi-value" style="color:#1e293b">$48.5K</div>
            <div class="kpi-detail">5 claims (1 severe)</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">Lost Productivity</div>
            <div class="kpi-value" style="color:#1e293b">$22.3K</div>
            <div class="kpi-detail">182 lost hours</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">Regulatory Risk</div>
            <div class="kpi-value" style="color:#1e293b">$15K</div>
            <div class="kpi-detail">OSHA fine exposure</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown("""<div class="kpi-card">
            <div class="kpi-label">Total Feb Cost</div>
            <div class="kpi-value" style="color:#dc2626">$85.8K</div>
            <div class="kpi-detail">Track cost per incident</div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── 3  Predictive Alerts (CALCULATED from real data) ──
    st.markdown(
        '<div class="section-hdr">Predictive Alerts --- Calculated from Data</div>',
        unsafe_allow_html=True)

    sorted_alerts = sorted(
        alerts.items(), key=lambda x: x[1]["trend_pct"], reverse=True)

    for yard_name, alert in sorted_alerts:
        trend_sign = "+" if alert["trend_pct"] >= 0 else ""
        days_so_far = today.day
        avg_str = f"{alert['daily_avg']:.1f}"
        st.markdown(f"""
        <div class="alert-box alert-{alert['level']}">
            <div class="alert-title" style="color:{alert['color']};">
                {yard_name}: {alert['label']} --- {trend_sign}{alert['trend_pct']:.0f}% vs {alert['prev_month']}
            </div>
            <div class="alert-body">
                {alert['current_month']}: <b>{alert['current']} events</b>
                in {days_so_far} days (avg {avg_str}/day)
                &nbsp;|&nbsp; {alert['prev_month']}: <b>{alert['previous']} events</b><br>
                Projected: <b>{alert['projected']} events</b> by {alert['month_end']}
                &nbsp;|&nbsp; Confidence: <b>{alert['confidence']}%</b>
            </div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── 4  Live Division Summary ──
    st.markdown(
        '<div class="section-hdr">Casing Division --- Live Summary</div>',
        unsafe_allow_html=True)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Motive Events", len(motive_display))
    s2.metric("Drivers Flagged", unique_drivers)
    s3.metric("Observations", len(observations_display))
    s4.metric("Incidents", len(incidents_display))
    s5.metric("Yards with Events",
              len(set(e["yard"] for e in motive_display if e.get("yard"))))

    st.write("")

    # ── 5  Division Drill-Downs (DETAILED TABLES) ──
    st.markdown(
        '<div class="section-hdr">Division Drill-Downs</div>',
        unsafe_allow_html=True)

    # Active filter indicator
    period_label = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    yard_label = selected_yard
    st.caption(
        f"Showing **{yard_label}** | **{time_period}** ({period_label}) "
        f"--- {len(incidents_display)} incidents, "
        f"{len(observations_display)} observations, "
        f"{len(motive_display)} driver events, "
        f"{len(audits_display)} rig audits")

    # --- Incidents table ---
    with st.expander(
        f"**KPA Incidents --- Casing: {len(incidents_display)}**",
        expanded=len(incidents_display) > 0,
    ):
        if incidents_display:
            inc_rows = [{
                "Report #": item.get("Report Number", ""),
                "Type": item.get("Incident Type", "---"),
                "Date": (item.get("Date") or "---")[:16],
                "District": item.get("_district", "---"),
                "Employee": item.get("Employee", "---"),
            } for item in incidents_display]

            st.dataframe(
                pd.DataFrame(inc_rows),
                use_container_width=True, hide_index=True)

            type_counts = Counter(r["Type"] for r in inc_rows)
            if len(type_counts) > 1:
                fig = go.Figure(go.Bar(
                    x=list(type_counts.values()),
                    y=list(type_counts.keys()),
                    orientation="h", marker_color=RED,
                ))
                fig.update_layout(
                    title="Incidents by Type",
                    height=max(200, len(type_counts) * 45),
                    margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No Casing Division incidents in this period.")

    # --- Observations table ---
    with st.expander(
        f"**KPA Observations --- Casing: {len(observations_display)}**",
    ):
        if observations_display:
            obs_rows = [{
                "Report #": item.get("Report Number", ""),
                "Type": item.get("Type of Observation", "---"),
                "Date": (item.get("Date") or "---")[:16],
                "District": item.get("_district", "---"),
                "Observer": item.get("Observer", "---"),
                "Description": ((item.get("Description of Observation") or "---")[:100]),
                "Location": item.get("Location / Task", "---"),
            } for item in observations_display]

            st.dataframe(
                pd.DataFrame(obs_rows),
                use_container_width=True, hide_index=True)

            obs_type_counts = Counter(r["Type"] for r in obs_rows)
            if obs_type_counts:
                fig = go.Figure(go.Pie(
                    labels=list(obs_type_counts.keys()),
                    values=list(obs_type_counts.values()),
                    hole=0.4,
                    marker=dict(colors=[
                        RED, BLUE, YELLOW, GREEN, "#7c3aed"]),
                ))
                fig.update_layout(
                    title="Observations by Type", height=300,
                    margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No Casing Division observations in this period.")

    # --- Driver Events table ---
    with st.expander(
        f"**Driver Events --- Motive: {len(motive_display)}**",
    ):
        if motive_display:
            drv_rows = []
            for evt in motive_display:
                speed = ""
                if evt.get("start_speed"):
                    speed = f"{evt['start_speed']:.0f} mph"
                    if evt.get("end_speed"):
                        speed += f" -> {evt['end_speed']:.0f} mph"
                drv_rows.append({
                    "Driver": evt.get("driver") or "Unknown",
                    "Event Type": evt["type"].replace("_", " ").title(),
                    "Date": evt.get("date_str", "---"),
                    "Vehicle": evt.get("vehicle", "---"),
                    "Location": (evt.get("location") or "---")[:50],
                    "Speed": speed,
                    "Yard": evt.get("yard") or "Unknown",
                })

            df_drv = pd.DataFrame(drv_rows)
            driver_order = {
                name: i for i, (name, _) in enumerate(drivers.most_common())}
            df_drv["_sort"] = df_drv["Driver"].map(
                lambda x: driver_order.get(x, 999))
            df_drv = df_drv.sort_values("_sort").drop("_sort", axis=1)
            st.dataframe(df_drv, use_container_width=True, hide_index=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if drivers:
                    top_drv = dict(drivers.most_common(10))
                    fig = go.Figure(go.Bar(
                        x=list(top_drv.values()),
                        y=list(top_drv.keys()),
                        orientation="h", marker_color=BLUE,
                    ))
                    fig.update_layout(
                        title="Top Drivers by Event Count",
                        height=max(250, len(top_drv) * 35),
                        margin=dict(l=20, r=20, t=40, b=20),
                        yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                if by_type:
                    fig = go.Figure(go.Pie(
                        labels=[t.replace("_", " ").title()
                                for t in by_type.keys()],
                        values=list(by_type.values()), hole=0.45,
                        marker=dict(colors=[
                            RED, BLUE, YELLOW, GREEN, "#7c3aed", "#e11d48"]),
                    ))
                    fig.update_layout(
                        title="Events by Type", height=300,
                        margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No Motive events in this period.")

    # --- Rig Audits (CSG - Safety Casing Field Assessment) ---
    with st.expander(
        f"**Rig Audits --- CSG Field Assessments: {len(audits_display)}**",
        expanded=len(audits_display) > 0,
    ):
        if audits_display:
            audit_rows = [{
                "Report #": a.get("Report Number", ""),
                "Date": (a.get("Date") or "---")[:16],
                "District": a.get("_district", "---"),
                "Rig": a.get("Rig", "---"),
                "Audit Type": a.get("Audit Type", "---"),
                "Observer": a.get("Observer", "---"),
                "Score": f"{a.get('_score', 0)}%",
                "Passed": a.get("_passed", 0),
                "Failed": a.get("_failed", 0),
                "Items Checked": a.get("_total_checked", 0),
            } for a in audits_display]

            st.dataframe(
                pd.DataFrame(audit_rows),
                use_container_width=True, hide_index=True)

            # Score gauge for each audit
            for a in audits_display:
                score = a.get("_score", 0)
                rig = a.get("Rig", "Unknown")
                district = a.get("_district", "Unknown")
                rpt = a.get("Report Number", "")
                audit_date = (a.get("Date") or "")[:10]
                observer = a.get("Observer", "---")
                score_color = (GREEN if score >= 90
                               else YELLOW if score >= 75 else RED)

                st.markdown(
                    f"---\n**{rig}** | {district} | {audit_date} | "
                    f"Auditor: {observer}")

                # Score bar
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    number={"suffix": "%"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": score_color},
                        "steps": [
                            {"range": [0, 75], "color": "#fee2e2"},
                            {"range": [75, 90], "color": "#fef3c7"},
                            {"range": [90, 100], "color": "#d1fae5"},
                        ],
                        "threshold": {
                            "line": {"color": DARK, "width": 2},
                            "thickness": 0.75, "value": 90,
                        },
                    },
                    title={"text": f"Audit Score --- {rig}"},
                ))
                fig.update_layout(
                    height=220,
                    margin=dict(l=30, r=30, t=60, b=20))
                st.plotly_chart(fig, use_container_width=True)

                # Failed items detail
                failed_items = a.get("_failed_items", [])
                if failed_items:
                    st.markdown(
                        f"**Failed Items ({len(failed_items)}):**")
                    for fi in failed_items:
                        st.write(f"- {fi}")
                else:
                    st.success("All checklist items passed.")

            # Summary charts if multiple audits
            if len(audits_display) > 1:
                st.markdown("---")
                col_a, col_b = st.columns(2)
                with col_a:
                    fig = go.Figure(go.Bar(
                        x=[a.get("Rig", "?") for a in audits_display],
                        y=[a.get("_score", 0) for a in audits_display],
                        marker_color=[
                            GREEN if a.get("_score", 0) >= 90
                            else YELLOW if a.get("_score", 0) >= 75
                            else RED for a in audits_display],
                        text=[f"{a.get('_score', 0)}%"
                              for a in audits_display],
                        textposition="outside",
                    ))
                    fig.update_layout(
                        title="Audit Scores by Rig",
                        yaxis=dict(range=[0, 105]),
                        height=300,
                        margin=dict(l=40, r=20, t=40, b=40))
                    fig.add_hline(
                        y=90, line_dash="dot", line_color=GREEN,
                        annotation_text="Target: 90%")
                    st.plotly_chart(fig, use_container_width=True)
                with col_b:
                    dist_counts = Counter(
                        a.get("_district", "?") for a in audits_display)
                    fig = go.Figure(go.Pie(
                        labels=list(dist_counts.keys()),
                        values=list(dist_counts.values()),
                        hole=0.4,
                    ))
                    fig.update_layout(
                        title="Audits by District", height=300,
                        margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No CSG rig audits in this period.")

    st.write("")

    # ── 6  Repeat Offenders ──
    st.markdown(
        '<div class="section-hdr">Repeat Offenders --- Live from Motive</div>',
        unsafe_allow_html=True)

    if drivers:
        driver_types = {}
        for evt in motive_display:
            name = evt.get("driver")
            if name:
                etype = evt["type"].replace("_", " ").title()
                driver_types.setdefault(name, Counter())[etype] += 1

        rows = []
        for name, total in drivers.most_common(10):
            top = driver_types.get(name, Counter()).most_common(1)
            violation = top[0][0] if top else "---"
            status = ("Coaching Needed" if total >= 3
                      else ("Monitor" if total >= 2 else "Low Risk"))
            rows.append({"Driver": name, "Top Violation": violation,
                         "Events": total, "Status": status})
        st.dataframe(pd.DataFrame(rows),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No driver-identified events in this period.")

    st.write("")

    # ── 7  Actions & Results ──
    st.markdown(
        '<div class="section-hdr">Actions &amp; Results'
        ' <span class="manual-tag">CURATED</span></div>',
        unsafe_allow_html=True)

    with st.expander("John Smith --- Speeding Coaching"):
        st.write("**Scheduled:** 2/19 &nbsp;|&nbsp; **Follow-up:** 2/26")
        st.warning("IN PROGRESS")
    with st.expander("Sarah Davis --- Coaching Completed"):
        st.write("Alerts reduced: 5x to 2x (60% improvement)")
        st.success("WORKING")
    with st.expander("Midland Root Cause --- Addressed"):
        st.write("Safety stand-down: 2/18 | Supervisor onboarding "
                 "intensified | Recovery expected: 2/25")
        st.success("COMPLETED")

    st.write("")

    # ── 8  Casing Yards Breakdown ──
    st.markdown(
        '<div class="section-hdr">Casing Yards Breakdown</div>',
        unsafe_allow_html=True)

    for yd in YARD_ORDER:
        yd_events = [e for e in motive_display if e.get("yard") == yd]
        yd_inc = [i for i in incidents_display if i.get("_district") == yd]
        yd_obs = [o for o in observations_display if o.get("_district") == yd]
        yd_alert = alerts.get(yd, {})

        with st.expander(
            f"**{yd} Yard** --- {len(yd_events)} events, "
            f"{len(yd_inc)} incidents, {len(yd_obs)} observations"
        ):
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Motive Events", len(yd_events))
            mc2.metric("Incidents", len(yd_inc))
            mc3.metric("Observations", len(yd_obs))

            if yd_alert:
                ts = "+" if yd_alert["trend_pct"] >= 0 else ""
                st.markdown(
                    f"**Trend:** {ts}{yd_alert['trend_pct']:.0f}% vs "
                    f"{yd_alert['prev_month']} | "
                    f"**Projected:** {yd_alert['projected']} by month-end | "
                    f"**Status:** {yd_alert['label']}")

            yd_drivers = Counter(
                e["driver"] for e in yd_events if e.get("driver"))
            if yd_drivers:
                st.markdown("**Flagged drivers:**")
                for dname, dcnt in yd_drivers.most_common(5):
                    st.write(
                        f"- {dname}: `{dcnt} event"
                        f"{'s' if dcnt > 1 else ''}`")
            else:
                st.caption("No driver-identified events for this yard.")

    st.write("")

    # ── 9  Overall Insights --- Charts ──
    st.markdown(
        '<div class="section-hdr">Overall Insights --- Live Data</div>',
        unsafe_allow_html=True)

    chart_l, chart_r = st.columns(2)

    with chart_l:
        if by_type:
            fig = go.Figure(go.Pie(
                labels=[t.replace("_", " ").title() for t in by_type],
                values=list(by_type.values()), hole=0.45,
                marker=dict(colors=[
                    RED, BLUE, YELLOW, GREEN, "#7c3aed", "#e11d48", "#0891b2"]),
                textinfo="label+percent", textposition="outside",
            ))
            fig.update_layout(
                title="Event Type Breakdown", height=340,
                margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with chart_r:
        if by_yard:
            fig = go.Figure(go.Bar(
                x=list(by_yard.keys()), y=list(by_yard.values()),
                marker_color=RED,
                text=list(by_yard.values()), textposition="outside",
            ))
            fig.update_layout(
                title="Events by Yard", height=340,
                margin=dict(l=40, r=20, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)

    # Events by day
    if by_day:
        st.markdown("**Motive Events by Day**")
        sorted_days = sorted(by_day.items())
        fig = go.Figure(go.Bar(
            x=[d[0] for d in sorted_days],
            y=[d[1] for d in sorted_days],
            marker_color=RED,
            text=[d[1] for d in sorted_days], textposition="outside",
        ))
        fig.update_layout(
            xaxis_title="Date", yaxis_title="Events",
            height=300, margin=dict(l=40, r=20, t=20, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Observations by day
    obs_daily = Counter()
    for item in observations_display:
        ds = item.get("Date", "")
        if ds and isinstance(ds, str) and len(ds) >= 10:
            obs_daily[ds[:10]] += 1
    if obs_daily:
        st.markdown("**KPA Observations by Day**")
        sorted_obs = sorted(obs_daily.items())
        fig = go.Figure(go.Bar(
            x=[d[0] for d in sorted_obs],
            y=[d[1] for d in sorted_obs],
            marker_color=BLUE,
            text=[d[1] for d in sorted_obs], textposition="outside",
        ))
        fig.update_layout(
            xaxis_title="Date", yaxis_title="Observations",
            height=300, margin=dict(l=40, r=20, t=20, b=40))
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
#  VIEW: INDIVIDUAL YARD
# =====================================================================

elif view_mode == "Individual Yard":

    if selected_yard == "All Yards":
        st.warning(
            "Please select a specific yard from the sidebar to use "
            "Individual Yard view.")
        st.stop()

    yard = selected_yard
    alert = alerts.get(yard, {})

    st.markdown(
        f'<div class="section-hdr">{yard} Yard --- Detail View</div>',
        unsafe_allow_html=True)

    # ── Yard KPIs ──
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Motive Events</div>
            <div class="kpi-value" style="color:{RED}">{len(motive_display)}</div>
            <div class="kpi-detail">{time_period}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Incidents</div>
            <div class="kpi-value" style="color:{DARK}">{len(incidents_display)}</div>
            <div class="kpi-detail">{time_period}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Observations</div>
            <div class="kpi-value" style="color:{BLUE}">{len(observations_display)}</div>
            <div class="kpi-detail">{time_period}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Drivers Flagged</div>
            <div class="kpi-value" style="color:{YELLOW}">{unique_drivers}</div>
            <div class="kpi-detail">{time_period}</div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── Yard Predictive Alert ──
    if alert:
        ts = "+" if alert["trend_pct"] >= 0 else ""
        st.markdown(f"""
        <div class="alert-box alert-{alert['level']}">
            <div class="alert-title" style="color:{alert['color']};">
                {yard}: {alert['label']} --- {ts}{alert['trend_pct']:.0f}% vs {alert['prev_month']}
            </div>
            <div class="alert-body">
                {alert['current_month']}: <b>{alert['current']} events</b>
                in {today.day} days (avg {alert['daily_avg']:.1f}/day)
                &nbsp;|&nbsp; {alert['prev_month']}: <b>{alert['previous']} events</b><br>
                Projected: <b>{alert['projected']} events</b> by {alert['month_end']}
                &nbsp;|&nbsp; Confidence: <b>{alert['confidence']}%</b>
            </div>
        </div>""", unsafe_allow_html=True)

    st.write("")

    # ── Tabs: Incidents | Observations | Drivers | Rig Audits ──
    tab_inc, tab_obs, tab_drv, tab_aud = st.tabs(
        ["Incidents", "Observations", "Driver Events", "Rig Audits"])

    with tab_inc:
        st.markdown(f"### {yard} --- Incidents ({len(incidents_display)})")
        if incidents_display:
            rows = [{
                "Report #": item.get("Report Number", ""),
                "Type": item.get("Incident Type", "---"),
                "Date": (item.get("Date") or "---")[:16],
                "Employee": item.get("Employee", "---"),
            } for item in incidents_display]
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True, hide_index=True)

            tc = Counter(r["Type"] for r in rows)
            if tc:
                fig = go.Figure(go.Bar(
                    x=list(tc.values()), y=list(tc.keys()),
                    orientation="h", marker_color=RED))
                fig.update_layout(
                    title=f"{yard} Incidents by Type",
                    height=max(200, len(tc) * 45),
                    margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success(f"No incidents for {yard} in this period.")

    with tab_obs:
        st.markdown(
            f"### {yard} --- Observations ({len(observations_display)})")
        if observations_display:
            rows = [{
                "Report #": item.get("Report Number", ""),
                "Type": item.get("Type of Observation", "---"),
                "Date": (item.get("Date") or "---")[:16],
                "Observer": item.get("Observer", "---"),
                "Description": (
                    (item.get("Description of Observation") or "---")[:100]),
                "Location": item.get("Location / Task", "---"),
            } for item in observations_display]
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True, hide_index=True)

            col_a, col_b = st.columns(2)
            with col_a:
                tc = Counter(r["Type"] for r in rows)
                if tc:
                    fig = go.Figure(go.Pie(
                        labels=list(tc.keys()),
                        values=list(tc.values()), hole=0.4))
                    fig.update_layout(
                        title=f"{yard} by Type", height=300,
                        margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                oc = Counter(r["Observer"] for r in rows)
                if oc:
                    fig = go.Figure(go.Bar(
                        x=list(oc.values()), y=list(oc.keys()),
                        orientation="h", marker_color=BLUE))
                    fig.update_layout(
                        title=f"{yard} by Observer",
                        height=max(200, len(oc) * 30),
                        margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.success(f"No observations for {yard} in this period.")

    with tab_drv:
        st.markdown(
            f"### {yard} --- Driver Events ({len(motive_display)})")
        if motive_display:
            rows = []
            for evt in motive_display:
                speed = ""
                if evt.get("start_speed"):
                    speed = f"{evt['start_speed']:.0f} mph"
                    if evt.get("end_speed"):
                        speed += f" -> {evt['end_speed']:.0f} mph"
                rows.append({
                    "Driver": evt.get("driver") or "Unknown",
                    "Event Type": evt["type"].replace("_", " ").title(),
                    "Date": evt.get("date_str", "---"),
                    "Vehicle": evt.get("vehicle", "---"),
                    "Speed": speed,
                    "Location": (evt.get("location") or "---")[:50],
                })
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True, hide_index=True)

            col_a, col_b = st.columns(2)
            with col_a:
                yd_drivers = Counter(
                    e["driver"] for e in motive_display if e.get("driver"))
                if yd_drivers:
                    fig = go.Figure(go.Bar(
                        x=list(yd_drivers.values()),
                        y=list(yd_drivers.keys()),
                        orientation="h", marker_color=YELLOW))
                    fig.update_layout(
                        title=f"{yard} --- Events by Driver",
                        height=max(200, len(yd_drivers) * 35),
                        margin=dict(l=20, r=20, t=40, b=20),
                        yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
            with col_b:
                yd_types = Counter(
                    e["type"].replace("_", " ").title()
                    for e in motive_display)
                if yd_types:
                    fig = go.Figure(go.Pie(
                        labels=list(yd_types.keys()),
                        values=list(yd_types.values()), hole=0.4))
                    fig.update_layout(
                        title=f"{yard} --- Events by Type", height=300,
                        margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No Motive events for {yard} in this period.")

    with tab_aud:
        st.markdown(
            f"### {yard} --- Rig Audits ({len(audits_display)})")
        if audits_display:
            rows = [{
                "Report #": a.get("Report Number", ""),
                "Date": (a.get("Date") or "---")[:16],
                "Rig": a.get("Rig", "---"),
                "Audit Type": a.get("Audit Type", "---"),
                "Observer": a.get("Observer", "---"),
                "Score": f"{a.get('_score', 0)}%",
                "Passed": a.get("_passed", 0),
                "Failed": a.get("_failed", 0),
            } for a in audits_display]
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True, hide_index=True)

            for a in audits_display:
                score = a.get("_score", 0)
                rig = a.get("Rig", "Unknown")
                audit_date = (a.get("Date") or "")[:10]
                observer = a.get("Observer", "---")
                score_color = (GREEN if score >= 90
                               else YELLOW if score >= 75 else RED)

                st.markdown(
                    f"---\n**{rig}** | {audit_date} | "
                    f"Auditor: {observer}")

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    number={"suffix": "%"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": score_color},
                        "steps": [
                            {"range": [0, 75], "color": "#fee2e2"},
                            {"range": [75, 90], "color": "#fef3c7"},
                            {"range": [90, 100], "color": "#d1fae5"},
                        ],
                        "threshold": {
                            "line": {"color": DARK, "width": 2},
                            "thickness": 0.75, "value": 90,
                        },
                    },
                    title={"text": f"Audit Score --- {rig}"},
                ))
                fig.update_layout(
                    height=220,
                    margin=dict(l=30, r=30, t=60, b=20))
                st.plotly_chart(fig, use_container_width=True)

                failed_items = a.get("_failed_items", [])
                if failed_items:
                    st.markdown(
                        f"**Failed Items ({len(failed_items)}):**")
                    for fi in failed_items:
                        st.write(f"- {fi}")
                else:
                    st.success("All checklist items passed.")
        else:
            st.info(f"No rig audits for {yard} in this period.")


# =====================================================================
#  VIEW: COMPARISON
# =====================================================================

elif view_mode == "Comparison":

    st.markdown(
        '<div class="section-hdr">Yard Comparison</div>',
        unsafe_allow_html=True)

    # Build comparison data (always uses date-filtered, all-yard data)
    comp_rows = []
    for yd in YARD_ORDER:
        yd_events = [e for e in motive_filtered if e.get("yard") == yd]
        yd_inc = [i for i in incidents_filtered if i.get("_district") == yd]
        yd_obs = [o for o in observations_filtered
                  if o.get("_district") == yd]
        yd_drv = len(set(e["driver"] for e in yd_events if e.get("driver")))
        a = alerts.get(yd, {})

        comp_rows.append({
            "Yard": yd,
            "Motive Events": len(yd_events),
            "Incidents": len(yd_inc),
            "Observations": len(yd_obs),
            "Drivers Flagged": yd_drv,
            "Trend": (f"{'+'if a.get('trend_pct', 0) >= 0 else ''}"
                      f"{a.get('trend_pct', 0):.0f}%"),
            "Projected": a.get("projected", 0),
            "Status": a.get("label", "---"),
        })

    st.dataframe(
        pd.DataFrame(comp_rows),
        use_container_width=True, hide_index=True)

    st.write("")

    # ── Performance Ranking ──
    st.markdown(
        '<div class="section-hdr">Performance Ranking</div>',
        unsafe_allow_html=True)

    ranked = sorted(
        comp_rows, key=lambda x: x["Motive Events"] + x["Incidents"])

    for i, row in enumerate(ranked):
        rank = i + 1
        medal = {1: "1st", 2: "2nd", 3: "3rd"}.get(rank, f"#{rank}")
        total = row["Motive Events"] + row["Incidents"]
        st.markdown(
            f"**{medal} {row['Yard']}** --- "
            f"{total} total events "
            f"({row['Motive Events']} Motive + {row['Incidents']} incidents) "
            f"| {row['Observations']} observations "
            f"| {row['Status']}")

    st.write("")

    # ── Comparison Charts ──
    st.markdown(
        '<div class="section-hdr">Comparison Charts</div>',
        unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        yards = [r["Yard"] for r in comp_rows]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Motive Events", x=yards,
            y=[r["Motive Events"] for r in comp_rows],
            marker_color=RED))
        fig.add_trace(go.Bar(
            name="Incidents", x=yards,
            y=[r["Incidents"] for r in comp_rows],
            marker_color=BLUE))
        fig.update_layout(
            title="Events & Incidents by Yard", barmode="group",
            height=350, margin=dict(l=40, r=20, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig = go.Figure(go.Bar(
            x=yards,
            y=[r["Observations"] for r in comp_rows],
            marker_color=GREEN,
            text=[r["Observations"] for r in comp_rows],
            textposition="outside",
        ))
        fig.update_layout(
            title="Observations by Yard", height=350,
            margin=dict(l=40, r=20, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Trend comparison
    st.markdown("**Trend Comparison (Current Month vs Previous)**")
    trend_yards = [r["Yard"] for r in comp_rows]
    trend_vals = [alerts.get(y, {}).get("trend_pct", 0)
                  for y in trend_yards]
    trend_colors = [alerts.get(y, {}).get("color", GRAY)
                    for y in trend_yards]

    fig = go.Figure(go.Bar(
        x=trend_yards, y=trend_vals,
        marker_color=trend_colors,
        text=[f"{v:+.0f}%" for v in trend_vals],
        textposition="outside",
    ))
    fig.update_layout(
        title="Month-over-Month Trend by Yard",
        yaxis_title="% Change", height=350,
        margin=dict(l=40, r=20, t=40, b=40))
    fig.add_hline(y=0, line_dash="dash", line_color=GRAY)
    fig.add_hline(y=30, line_dash="dot", line_color=RED,
                  annotation_text="High Risk (+30%)")
    fig.add_hline(y=-10, line_dash="dot", line_color=GREEN,
                  annotation_text="Improving (-10%)")
    st.plotly_chart(fig, use_container_width=True)


# =====================================================================
#  FOOTER
# =====================================================================

st.divider()
st.markdown(
    f'<div class="footer-text">'
    f'Data fetched: {fetched_str} &bull; '
    f'BRHAS Safety Dashboard &bull; '
    f'Butch&#39;s Companies'
    f'</div>', unsafe_allow_html=True)
