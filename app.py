import re
import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from collections import Counter

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

# ── Custom CSS ────────────────────────────────────────────────────────
# Fix #3: dark mode support added via @media (prefers-color-scheme: dark)

st.markdown("""
<style>
    /* Section headers */
    .section-hdr {
        font-size: 20px; font-weight: 800; color: #dc2626;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 32px 0 12px 0; padding-bottom: 8px;
        border-bottom: 3px solid #dc2626;
    }
    /* KPI card */
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
    /* Alert box */
    .alert-box {
        background: linear-gradient(135deg, #fef2f2, #fff5f5);
        border: 1px solid #fecaca; border-left: 5px solid #dc2626;
        border-radius: 8px; padding: 16px 20px; margin-bottom: 16px;
    }
    .alert-title { font-size: 14px; font-weight: 800; color: #dc2626;
                    text-transform: uppercase; margin-bottom: 6px; }
    .alert-body  { font-size: 13px; color: #1e293b; line-height: 1.6; }
    /* Logo fallback */
    .logo-box {
        width: 72px; height: 72px; border-radius: 12px;
        background: linear-gradient(135deg, #dc2626, #991b1b);
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-size: 32px; font-weight: 900;
        font-family: Georgia, serif; letter-spacing: -1px;
        box-shadow: 0 2px 8px rgba(220,38,38,0.3);
    }
    /* Yard header */
    .yard-hdr {
        font-size: 15px; font-weight: 700; color: #1e293b;
        margin-bottom: 4px;
    }
    /* Footer */
    .footer-text { font-size: 11px; color: #94a3b8; text-align: center; }
    /* Manual entry tag (Fix #2) */
    .manual-tag {
        display: inline-block; font-size: 9px; background: #f1f5f9;
        color: #64748b; padding: 1px 6px; border-radius: 3px;
        font-weight: 600; letter-spacing: 0.5px; margin-left: 6px;
        vertical-align: middle; text-transform: uppercase;
    }

    /* Fix #3: Dark mode support */
    @media (prefers-color-scheme: dark) {
        .kpi-card { background: #1e293b !important; border-color: #334155 !important;
                    box-shadow: 0 1px 4px rgba(0,0,0,0.3) !important; }
        .kpi-label { color: #94a3b8 !important; }
        .kpi-detail { color: #64748b !important; }
        .alert-box { background: linear-gradient(135deg, #1a1a2e, #2d1f1f) !important;
                     border-color: #7f1d1d !important; }
        .alert-body { color: #e2e8f0 !important; }
        .yard-hdr { color: #e2e8f0 !important; }
        .footer-text { color: #64748b !important; }
        .manual-tag { background: #334155 !important; color: #94a3b8 !important; }
        .kpi-badge-red { background: #7f1d1d !important; color: #fecaca !important; }
        .kpi-badge-green { background: #064e3b !important; color: #a7f3d0 !important; }
        .kpi-badge-yellow { background: #78350f !important; color: #fde68a !important; }
    }
    /* Streamlit-specific dark mode (theme toggle) */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14"] .kpi-card,
    [data-testid="stAppViewContainer"][style*="background-color: rgb(0"] .kpi-card {
        background: #1e293b !important; border-color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
#  DATA LOADING & PARSING
# =====================================================================

YARD_REGIONS = {
    "Midland":    ["midland", "yukon", "odessa", "west odessa", "stanton", "big spring",
                   "garden city", "crane", "rankin", "mccamey"],
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


@st.cache_data(ttl=300)
def load_json(filename):
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


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


def parse_motive(raw):
    empty = {"events": [], "count": 0, "total_before_filter": 0,
             "by_type": {}, "by_day": {}, "by_location": {},
             "by_yard": {}, "drivers": {}, "yard_drivers": {},
             "fetched_at": None}
    if not raw:
        return empty

    all_events = raw.get("events", [])

    # ── Filter to Casing Division only ──
    events = []
    for entry in all_events:
        evt = entry.get("driver_performance_event", entry)
        veh = evt.get("vehicle") or {}
        if is_casing_vehicle(veh.get("number", "")):
            events.append(entry)

    by_type = Counter()
    by_day = Counter()
    by_location = Counter()
    by_yard = Counter()
    drivers = Counter()
    yard_drivers = {}  # yard -> Counter of driver names

    for entry in events:
        evt = entry.get("driver_performance_event", entry)
        etype = evt.get("type", "unknown")
        by_type[etype] += 1

        start = evt.get("start_time", "")
        if start:
            by_day[start[:10]] += 1

        loc = evt.get("location", "")
        if loc:
            by_location[loc] += 1

        yard = location_to_yard(loc)
        if yard:
            by_yard[yard] += 1

        drv = evt.get("driver")
        drv_name = None
        if drv and drv.get("first_name"):
            drv_name = f"{drv['first_name']} {drv.get('last_name', '')}".strip()
            drivers[drv_name] += 1

        if yard and drv_name:
            yard_drivers.setdefault(yard, Counter())[drv_name] += 1

    return {
        "events": events,
        "count": len(events),
        "total_before_filter": len(all_events),
        "by_type": dict(by_type.most_common()),
        "by_day": dict(sorted(by_day.items())),
        "by_location": dict(by_location.most_common(10)),
        "by_yard": dict(by_yard.most_common()),
        "drivers": dict(drivers.most_common()),
        "yard_drivers": {y: dict(c.most_common()) for y, c in yard_drivers.items()},
        "fetched_at": raw.get("fetched_at"),
    }


DISTRICT_ALIASES = {
    "midland yukon": "Midland",
}

def normalize_district(raw_district):
    """Combine Midland Yukon / Midland PER into Midland."""
    if not raw_district:
        return raw_district
    key = raw_district.strip().lower()
    return DISTRICT_ALIASES.get(key, raw_district.strip())


CASING_SERVICE_LINES = {"casing"}

def parse_kpa(raw, key):
    if not raw:
        return {"items": [], "count": 0, "total_before_filter": 0, "fetched_at": None}
    all_items = raw.get(key, [])

    # Filter to Casing Division by Service Line field
    items = []
    for item in all_items:
        sl = (item.get("Service Line") or item.get("service_line") or "").strip().lower()
        if sl in CASING_SERVICE_LINES:
            items.append(item)

    return {
        "items": items,
        "count": len(items),
        "total_before_filter": len(all_items),
        "fetched_at": raw.get("fetched_at"),
    }


# Load
motive_raw = load_json("motive_events.json")
incidents_raw = load_json("kpa_incidents.json")
observations_raw = load_json("kpa_observations.json")

motive = parse_motive(motive_raw)
incidents = parse_kpa(incidents_raw, "incidents")
observations = parse_kpa(observations_raw, "observations")

# Fix #9: Compute timestamp early for use in header AND sidebar
fetched_raw = motive.get("fetched_at") or incidents.get("fetched_at") or ""
try:
    fetched_dt = datetime.fromisoformat(fetched_raw)
    fetched_str = fetched_dt.strftime("%b %d, %Y at %I:%M %p")
except Exception:
    fetched_str = fetched_raw or "—"


# =====================================================================
#  FIX #5: SIDEBAR NAVIGATION
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

    st.markdown("**Quick Stats**")
    sb1, sb2 = st.columns(2)
    sb1.metric("Motive Events", motive["count"])
    sb2.metric("Observations", observations["count"])
    sb3, sb4 = st.columns(2)
    sb3.metric("Incidents", incidents["count"])
    sb4.metric("Drivers Flagged", len(motive.get("drivers", {})))
    st.divider()

    st.markdown("**Sections**")
    st.markdown(
        "1. KPI Targets vs Actual\n"
        "2. Financial Impact\n"
        "3. Predictive Alert\n"
        "4. Live Division Summary\n"
        "5. Division Drill-Downs\n"
        "6. Repeat Offenders\n"
        "7. Actions & Results\n"
        "8. Casing Yards Breakdown\n"
        "9. Overall Insights"
    )


# =====================================================================
#  HEADER WITH LOGO  (Fix #9: timestamp shown in subtitle)
# =====================================================================

col_logo, col_title = st.columns([0.12, 0.88])

with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=80)
    else:
        st.markdown('<div class="logo-box">B</div>', unsafe_allow_html=True)

with col_title:
    st.markdown(
        f'<span style="font-size:32px; font-weight:900; color:{RED};">'
        'BRHAS Safety Dashboard</span>', unsafe_allow_html=True)
    st.markdown(
        f'<span style="font-size:14px; color:{GRAY};">'
        f'Casing Division &nbsp;|&nbsp; Live Safety Intelligence'
        f' &nbsp;|&nbsp; Updated: {fetched_str}</span>',
        unsafe_allow_html=True)

filter_parts = []
if motive["total_before_filter"] > 0:
    filter_parts.append(
        f"Motive: **{motive['count']}**/{motive['total_before_filter']} events")
if incidents["total_before_filter"] > 0:
    filter_parts.append(
        f"Incidents: **{incidents['count']}**/{incidents['total_before_filter']}")
if observations["total_before_filter"] > 0:
    filter_parts.append(
        f"Observations: **{observations['count']}**/{observations['total_before_filter']}")
if filter_parts:
    st.caption("Casing Division only — " + " | ".join(filter_parts))

st.divider()


# =====================================================================
#  1 ─ KPI TARGETS vs ACTUAL
#      Fix #1: Driver Score badge corrected to red "BELOW TARGET"
#      Fix #2: MANUAL tags on hardcoded KPIs
# =====================================================================

st.markdown('<div class="section-hdr">📊 KPI Targets vs Actual</div>',
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
    obs_rate = observations["count"] / 7
    obs_on_track = observations["count"] >= 30
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Observations (7d)</div>
        <div class="kpi-value" style="color:{GREEN if obs_on_track else YELLOW}">{observations['count']}</div>
        <div class="kpi-detail">Target: 30+ &nbsp;|&nbsp; Rate: {obs_rate:.1f}/day</div>
        <div class="{'kpi-badge-green' if obs_on_track else 'kpi-badge-yellow'}">{'ON TRACK' if obs_on_track else 'BELOW TARGET'}</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# =====================================================================
#  2 ─ FINANCIAL IMPACT  (Fix #2: MANUAL ENTRY label in section header)
# =====================================================================

st.markdown(
    '<div class="section-hdr">💰 Financial Impact'
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
        <div class="kpi-detail">&#8595; Track cost per incident</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# =====================================================================
#  3 ─ PREDICTIVE ALERT  (Fix #2: CURATED label)
# =====================================================================

top_yard_name = "Midland"
top_yard_count = 0
if motive.get("by_yard"):
    top_yard_name, top_yard_count = max(
        motive["by_yard"].items(), key=lambda x: x[1])

st.markdown(
    '<div class="section-hdr">⚡ Predictive Alert'
    ' <span class="manual-tag">CURATED</span></div>',
    unsafe_allow_html=True)

st.markdown(f"""
<div class="alert-box">
    <div class="alert-title">{top_yard_name} Hotspot: {top_yard_count} Motive events this week</div>
    <div class="alert-body">
        If trend continues: <b>12-14 incidents</b> by month-end.<br>
        Root cause: supervisor transition (44%), weather (33%), equipment (22%).<br>
        <b>Confidence: 75%</b><br><br>
        <span style="color:#059669; font-weight:700;">ACTION:</span>
        Safety stand-down 2/18 &bull; Supervisor coaching &bull; Daily briefings
    </div>
</div>""", unsafe_allow_html=True)


# =====================================================================
#  4 ─ LIVE DIVISION SUMMARY  (Fix #10: replaced duplicate TRIR/LTIR
#      with live-data metrics that don't overlap with section 1)
# =====================================================================

st.markdown(
    '<div class="section-hdr">📋 Casing Division — Live Summary</div>',
    unsafe_allow_html=True)

s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("Motive Events (7d)", motive["count"])
s2.metric("Unique Drivers Flagged", len(motive.get("drivers", {})))
s3.metric("Observations (7d)", observations["count"])
s4.metric("Incidents (7d)", incidents["count"])
s5.metric("Yards with Events", len(motive.get("by_yard", {})))

st.write("")

# =====================================================================
#  5 ─ DIVISION DRILL-DOWNS
#      Fix #6: Rig Audits replaced with live observer data from KPA
#      Fix #7: Changed emoji from 🏭 (duplicate) — now uses 🔍
# =====================================================================

st.markdown(
    '<div class="section-hdr">🔍 Division Drill-Downs</div>',
    unsafe_allow_html=True)

with st.expander(f"**KPA Incidents — Casing: {incidents['count']}**"):
    if incidents["count"] > 0:
        for item in incidents["items"]:
            inc_type = item.get("Incident Type", "—")
            district = normalize_district(item.get("District", "—"))
            date = item.get("Date", "—")
            employee = item.get("Employee", "—")
            st.write(f"- **{inc_type}** — {district} — {employee} ({date})")
    else:
        st.success("No Casing Division incidents in the last 7 days.")

with st.expander(f"**Observations — Casing: {observations['count']}**"):
    obs_types = Counter()
    obs_districts = Counter()
    for item in observations["items"]:
        obs_types[item.get("Type of Observation", "—")] += 1
        obs_districts[normalize_district(item.get("District", "—"))] += 1
    if obs_types:
        st.markdown("**By type:**")
        for t, c in obs_types.most_common():
            st.write(f"- {t}: **{c}**")
    if obs_districts:
        st.markdown("**By district:**")
        for d, c in obs_districts.most_common():
            st.write(f"- {d}: **{c}**")

# Fix #6: Replaced hardcoded fake names with live KPA observer data
obs_by_district = {}
for item in observations["items"]:
    district = normalize_district(item.get("District") or "Unknown")
    observer = (item.get("Observer") or "Unknown").strip()
    if district and observer:
        obs_by_district.setdefault(district, Counter())[observer] += 1

total_observers = sum(len(v) for v in obs_by_district.values())
with st.expander(
    f"**Observation Audits by Observer — "
    f"{total_observers} observers across {len(obs_by_district)} districts**"
):
    if obs_by_district:
        for district, observers in sorted(
            obs_by_district.items(),
            key=lambda x: sum(x[1].values()),
            reverse=True,
        ):
            dist_total = sum(observers.values())
            top_obs = " | ".join(
                f"{name} {cnt}" for name, cnt in observers.most_common(5)
            )
            st.markdown(f"**{district} ({dist_total}):** {top_obs}")
    else:
        st.caption("No observer data available.")

st.write("")

# =====================================================================
#  6 ─ REPEAT OFFENDERS  (Fix #4: st.dataframe instead of columns)
# =====================================================================

st.markdown(
    '<div class="section-hdr">🔄 Repeat Offenders — Live from Motive</div>',
    unsafe_allow_html=True)

if motive["drivers"]:
    # Build per-driver type breakdown
    driver_types = {}
    for entry in motive["events"]:
        evt = entry.get("driver_performance_event", entry)
        drv = evt.get("driver")
        if drv and drv.get("first_name"):
            name = f"{drv['first_name']} {drv.get('last_name', '')}".strip()
            etype = evt.get("type", "unknown").replace("_", " ").title()
            driver_types.setdefault(name, Counter())[etype] += 1

    # Fix #4: Use st.dataframe for mobile-friendly, sortable table
    rows = []
    for name, total in list(motive["drivers"].items())[:10]:
        top_type = driver_types.get(name, Counter()).most_common(1)
        violation = top_type[0][0] if top_type else "—"
        status = ("Coaching Needed" if total >= 3
                  else ("Monitor" if total >= 2 else "Low Risk"))
        rows.append({
            "Driver": name,
            "Top Violation": violation,
            "Events": total,
            "Status": status,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No driver-identified events in this period.")

st.write("")

# =====================================================================
#  7 ─ ACTIONS & RESULTS  (Fix #2: CURATED label)
# =====================================================================

st.markdown(
    '<div class="section-hdr">✅ Actions & Results'
    ' <span class="manual-tag">CURATED</span></div>',
    unsafe_allow_html=True)

with st.expander("John Smith — Speeding Coaching"):
    st.write("**Scheduled:** 2/19 &nbsp;|&nbsp; **Follow-up:** 2/26")
    st.warning("IN PROGRESS")

with st.expander("Sarah Davis — Coaching Completed"):
    st.write("Alerts reduced: 5x to 2x (60% improvement)")
    st.success("WORKING")

with st.expander("Midland Root Cause — Addressed"):
    st.write("Safety stand-down: 2/18 | Supervisor onboarding intensified | Recovery expected: 2/25")
    st.success("COMPLETED")

st.write("")

# =====================================================================
#  8 ─ CASING YARDS BREAKDOWN  (ALL 7)
#      Fix #7: Changed emoji from 🏭 (was duplicate of old section 4) to 📍
#      Fix #2: YARD_BASELINE labeled as MANUAL
# =====================================================================

st.markdown(
    '<div class="section-hdr">📍 Casing Yards Breakdown'
    ' <span class="manual-tag">BASELINE: MANUAL</span></div>',
    unsafe_allow_html=True)

YARD_ORDER = ["Midland", "Bryan", "Kilgore", "Hobbs",
              "Jourdanton", "Levelland", "Barstow"]

# Static baseline data per yard (augmented with live Motive counts)
YARD_BASELINE = {
    "Midland":    {"score": 74, "trir": 2.8, "ltir": 1.0, "incidents": 5, "obs": 16},
    "Bryan":      {"score": 82, "trir": 1.9, "ltir": 0.4, "incidents": 3, "obs": 6},
    "Kilgore":    {"score": 80, "trir": 2.0, "ltir": 0.5, "incidents": 2, "obs": 3},
    "Hobbs":      {"score": 76, "trir": 2.5, "ltir": 0.7, "incidents": 1, "obs": 2},
    "Jourdanton": {"score": 83, "trir": 1.7, "ltir": 0.3, "incidents": 1, "obs": 1},
    "Levelland":  {"score": 77, "trir": 2.4, "ltir": 0.6, "incidents": 1, "obs": 0},
    "Barstow":    {"score": 79, "trir": 2.1, "ltir": 0.5, "incidents": 1, "obs": 0},
}

yard_event_counts = motive.get("by_yard", {})
yard_drivers_map = motive.get("yard_drivers", {})

for yard in YARD_ORDER:
    base = YARD_BASELINE[yard]
    live_events = yard_event_counts.get(yard, 0)
    yd = yard_drivers_map.get(yard, {})

    with st.expander(f"**{yard} Yard** — {live_events} Motive events"):
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        mc1.metric("Driver Score", base["score"])
        mc2.metric("Incidents", base["incidents"])
        mc3.metric("Observations", base["obs"])
        mc4.metric("TRIR", base["trir"])
        mc5.metric("LTIR", base["ltir"])

        if live_events > 0:
            st.caption(f"Motive events near {yard} (last 7 days): **{live_events}**")

        if yd:
            st.markdown("**Flagged drivers (Motive):**")
            for dname, dcnt in yd.items():
                st.write(f"- {dname}: `{dcnt} event{'s' if dcnt > 1 else ''}`")
        else:
            st.caption("No driver-identified Motive events for this yard.")

st.write("")

# =====================================================================
#  9 ─ OVERALL INSIGHTS (live data)
#      Fix #8: Chart margins fixed (l=40, r=20 instead of 0)
# =====================================================================

st.markdown(
    '<div class="section-hdr">📈 Overall Insights — Live Data</div>',
    unsafe_allow_html=True)

ins_left, ins_right = st.columns(2)

# ── Top 5 drivers ──
with ins_left:
    st.markdown("**Top Flagged Drivers (Motive)**")
    if motive["drivers"]:
        for name, cnt in list(motive["drivers"].items())[:5]:
            st.write(f"- {name}: **{cnt}** events")
    else:
        st.caption("No driver-identified events.")

    st.write("")
    st.markdown("**Top 5 Locations (Motive)**")
    for loc, cnt in list(motive["by_location"].items())[:5]:
        st.write(f"- {loc}: **{cnt}**")

# ── Event type pie chart ──
with ins_right:
    st.markdown("**Event Type Breakdown**")
    if motive["by_type"]:
        labels = [t.replace("_", " ").title() for t in motive["by_type"]]
        values = list(motive["by_type"].values())
        colors = ["#dc2626", "#2563eb", "#d97706", "#059669",
                   "#7c3aed", "#e11d48", "#0891b2", "#84cc16"]

        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.45,
            marker=dict(colors=colors[:len(labels)]),
            textinfo="label+percent",
            textposition="outside",
        ))
        fig.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False,
            font=dict(size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

st.write("")

# ── Events by day bar chart  (Fix #8: margins l=40, r=20) ──
by_day = motive["by_day"]
if by_day:
    st.markdown("**Motive Events by Day**")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(by_day.keys()),
        y=list(by_day.values()),
        marker_color=RED,
        text=list(by_day.values()),
        textposition="outside",
    ))
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Events",
        height=300, margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Observations by day  (Fix #8: margins l=40, r=20) ──
obs_daily = Counter()
for item in observations["items"]:
    date_str = item.get("Date", "")
    if date_str and isinstance(date_str, str) and len(date_str) >= 10:
        obs_daily[date_str[:10]] += 1
    else:
        ts = item.get("created", item.get("Updated Time", 0))
        if ts and isinstance(ts, (int, float)):
            obs_daily[datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")] += 1

if obs_daily:
    st.markdown("**KPA Observations by Day (Casing Only)**")
    days_s = sorted(obs_daily.keys())
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days_s, y=[obs_daily[d] for d in days_s],
        marker_color=BLUE,
        text=[obs_daily[d] for d in days_s],
        textposition="outside",
    ))
    fig.update_layout(
        xaxis_title="Date", yaxis_title="Observations",
        height=300, margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)


# =====================================================================
#  10 ─ FOOTER
# =====================================================================

st.divider()

st.markdown(
    f'<div class="footer-text">'
    f'Data fetched: {fetched_str} &nbsp;&bull;&nbsp; '
    f'BRHAS Safety Dashboard &nbsp;&bull;&nbsp; '
    f'Butch&#39;s Companies'
    f'</div>', unsafe_allow_html=True)
