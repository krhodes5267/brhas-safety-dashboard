import streamlit as st
import json
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from collections import Counter

# Page config
st.set_page_config(
    page_title="BRHAS Safety Dashboard",
    page_icon="🏭",
    layout="wide",
)

DATA_DIR = Path(__file__).parent / "data"


# ── Data loading ──────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_json(filename):
    path = DATA_DIR / filename
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def parse_motive(raw):
    """Extract useful summaries from Motive event data."""
    if not raw:
        return {"events": [], "count": 0, "by_type": {}, "by_day": {},
                "by_location": {}, "drivers": {}, "fetched_at": None}

    events = raw.get("events", [])
    by_type = Counter()
    by_day = Counter()
    by_location = Counter()
    drivers = Counter()

    for entry in events:
        evt = entry.get("driver_performance_event", entry)
        by_type[evt.get("type", "unknown")] += 1

        start = evt.get("start_time", "")
        if start:
            by_day[start[:10]] += 1

        loc = evt.get("location")
        if loc:
            by_location[loc] += 1

        drv = evt.get("driver")
        if drv and drv.get("first_name"):
            name = f"{drv['first_name']} {drv.get('last_name', '')}".strip()
            drivers[name] += 1

    return {
        "events": events,
        "count": len(events),
        "by_type": dict(by_type.most_common()),
        "by_day": dict(sorted(by_day.items())),
        "by_location": dict(by_location.most_common(10)),
        "drivers": dict(drivers.most_common()),
        "fetched_at": raw.get("fetched_at"),
    }


def parse_kpa(raw, key):
    """Extract count and timestamps from KPA data."""
    if not raw:
        return {"items": [], "count": 0, "fetched_at": None}
    items = raw.get(key, [])
    return {
        "items": items,
        "count": len(items),
        "fetched_at": raw.get("fetched_at"),
    }


# ── Load everything ───────────────────────────────────────────────────

motive_raw = load_json("motive_events.json")
incidents_raw = load_json("kpa_incidents.json")
observations_raw = load_json("kpa_observations.json")

motive = parse_motive(motive_raw)
incidents = parse_kpa(incidents_raw, "incidents")
observations = parse_kpa(observations_raw, "observations")

no_data = motive["count"] == 0 and incidents["count"] == 0 and observations["count"] == 0

# ── Header ────────────────────────────────────────────────────────────

st.title("🏭 BRHAS Safety Dashboard")
st.caption("Casing Division | Live Safety Intelligence")

if no_data:
    st.warning(
        "No live data found. Run `python fetch_live_data.py` to pull "
        "from Motive & KPA EHS APIs."
    )
st.divider()

# ── KPI Summary ───────────────────────────────────────────────────────

st.subheader("📊 Live KPI Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Motive Events (7 d)", motive["count"])
col2.metric("KPA Incidents (7 d)", incidents["count"])
col3.metric("KPA Observations (7 d)", observations["count"])

event_types = motive["by_type"]
driver_event_count = sum(1 for e in motive["events"]
                         if (e.get("driver_performance_event", e).get("driver")))
col4.metric("Events w/ Driver ID", driver_event_count)

# ── Motive Event Breakdown ────────────────────────────────────────────

st.subheader("🚗 Motive Driver Events — Last 7 Days")

if event_types:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Event Types**")
        for etype, cnt in event_types.items():
            label = etype.replace("_", " ").title()
            st.write(f"- {label}: **{cnt}**")

    with col2:
        fig = go.Figure(go.Pie(
            labels=[t.replace("_", " ").title() for t in event_types],
            values=list(event_types.values()),
            hole=0.4,
        ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
            showlegend=True,
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No Motive events in this period.")

# ── Events-by-Day Chart ──────────────────────────────────────────────

by_day = motive["by_day"]
if by_day:
    st.subheader("📈 Events by Day")
    days = list(by_day.keys())
    counts = list(by_day.values())

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days, y=counts,
        marker_color="#dc2626",
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Events",
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Top Locations ─────────────────────────────────────────────────────

locations = motive["by_location"]
if locations:
    st.subheader("📍 Top Locations")
    cols = st.columns(min(len(locations), 5))
    for i, (loc, cnt) in enumerate(list(locations.items())[:5]):
        cols[i].metric(loc, cnt)

# ── Driver Leaderboard ────────────────────────────────────────────────

driver_counts = motive["drivers"]
if driver_counts:
    st.subheader("👤 Drivers with Most Events")
    st.caption("Drivers identified in Motive events (lower is better)")
    for name, cnt in list(driver_counts.items())[:10]:
        c1, c2 = st.columns([0.7, 0.3])
        c1.write(f"**{name}**")
        c2.write(f"`{cnt} event{'s' if cnt != 1 else ''}`")

# ── KPA Incidents ─────────────────────────────────────────────────────

st.subheader("🔴 KPA Incidents — Last 7 Days")

if incidents["count"] > 0:
    st.metric("Total Incidents", incidents["count"])
    with st.expander("Incident IDs"):
        for item in incidents["items"]:
            ts = item.get("created", 0)
            dt = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M") if ts else "—"
            st.write(f"- ID **{item['id']}** — created {dt}")
else:
    st.success("No incidents reported in the last 7 days.")

# ── KPA Observations ─────────────────────────────────────────────────

st.subheader("👁 KPA Observations — Last 7 Days")

if observations["count"] > 0:
    st.metric("Total Observations", observations["count"])

    # Group observations by day
    obs_by_day = Counter()
    for item in observations["items"]:
        ts = item.get("created", 0)
        if ts:
            day = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
            obs_by_day[day] += 1

    if obs_by_day:
        days_sorted = sorted(obs_by_day.keys())
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=days_sorted,
            y=[obs_by_day[d] for d in days_sorted],
            marker_color="#2563eb",
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Observations",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No observations in the last 7 days.")

# ── Footer ────────────────────────────────────────────────────────────

st.divider()
fetched = motive.get("fetched_at") or incidents.get("fetched_at") or "—"
st.caption(f"Data fetched at: {fetched} | BRHAS Safety Dashboard")
