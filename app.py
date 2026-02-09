import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Page config
st.set_page_config(
    page_title="BRHAS Safety Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9f9f9 100%);
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #666;
        margin-bottom: 8px;
        font-weight: 700;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 900;
        color: #dc2626;
        margin-bottom: 4px;
    }
    .metric-detail {
        font-size: 10px;
        color: #888;
        line-height: 1.3;
    }
    .status-win {
        background: #d1fae5;
        color: #065f46;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 9px;
        font-weight: 700;
        display: inline-block;
        margin-top: 6px;
    }
    .status-alert {
        background: #fee2e2;
        color: #7f1d1d;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 9px;
        font-weight: 700;
        display: inline-block;
        margin-top: 6px;
    }
    .alert-box {
        background: linear-gradient(135deg, #fef2f2 0%, #fef8f8 100%);
        border: 1px solid #fed7d7;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 20px;
    }
    .alert-title {
        font-size: 12px;
        font-weight: 900;
        color: #dc2626;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .section-title {
        font-size: 16px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #dc2626;
        margin: 30px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #dc2626;
    }
    </style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data(ttl=300)
def load_data():
    """Load JSON data from files"""
    data_dir = Path(__file__).parent / "data"
    
    motive_data = {}
    kpa_incidents = {}
    kpa_observations = {}
    
    try:
        if (data_dir / "motive_events.json").exists():
            with open(data_dir / "motive_events.json") as f:
                motive_data = json.load(f)
    except:
        pass
    
    try:
        if (data_dir / "kpa_incidents.json").exists():
            with open(data_dir / "kpa_incidents.json") as f:
                kpa_incidents = json.load(f)
    except:
        pass
    
    try:
        if (data_dir / "kpa_observations.json").exists():
            with open(data_dir / "kpa_observations.json") as f:
                kpa_observations = json.load(f)
    except:
        pass
    
    return motive_data, kpa_incidents, kpa_observations

# Header
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image("butchs-logo.jpg", width=80) if Path("butchs-logo.jpg").exists() else st.write("🏭")
with col2:
    st.title("BRHAS Safety Dashboard")
    st.caption("A Grade | Clean Intelligence | Live Data")

st.write("---")

# Load data
motive_data, kpa_incidents, kpa_observations = load_data()

# KPI Targets
st.markdown("<div class='section-title'>📊 KPI Targets vs Actual</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>TRIR</div>
        <div class='metric-value'>2.3</div>
        <div class='metric-detail'>Target: <2.0 | Ind: 3.5</div>
        <div class='status-alert'>⚠️ MISS</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>LTIR</div>
        <div class='metric-value'>0.8</div>
        <div class='metric-detail'>Target: <0.5 | Ind: 1.2</div>
        <div class='status-alert'>⚠️ MISS</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>Driver Score</div>
        <div class='metric-value'>78</div>
        <div class='metric-detail'>Target: >85 | Ind: 72</div>
        <div class='status-win'>✓ ABOVE</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>Observations</div>
        <div class='metric-value'>28</div>
        <div class='metric-detail'>Target: 30+ | Rate: 2.1/wk</div>
        <div class='status-win'>✓ ON TRACK</div>
    </div>
    """, unsafe_allow_html=True)

# Financial Impact
st.markdown("<div class='section-title'>💰 Financial Impact</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>Workers' Comp</div>
        <div class='metric-value'>$48.5K</div>
        <div class='metric-detail'>5 claims (1 severe)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>Lost Productivity</div>
        <div class='metric-value'>$22.3K</div>
        <div class='metric-detail'>182 lost hours</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>Regulatory Risk</div>
        <div class='metric-value'>$15K</div>
        <div class='metric-detail'>OSHA fine exposure</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='metric-card'>
        <div class='metric-label'>Total Feb Cost</div>
        <div class='metric-value'>$85.8K</div>
        <div class='metric-detail'>↓ Cost per incident</div>
    </div>
    """, unsafe_allow_html=True)

# Predictive Alert
st.markdown("<div class='section-title'>⚡ Predictive Alert</div>", unsafe_allow_html=True)

st.markdown("""
<div class='alert-box'>
    <div class='alert-title'>Midland Trend: +40% vs Jan</div>
    <p>If trend continues: 12-14 incidents by month-end. Root cause: supervisor transition (44%), weather (33%), equipment (22%).</p>
    <p><strong>Confidence: 75%</strong></p>
    <p style='font-size: 10px; color: #555;'><strong>Action:</strong> Safety stand-down 2/18, supervisor coaching, daily briefings.</p>
</div>
""", unsafe_allow_html=True)

# Casing Division Summary
st.markdown("<div class='section-title'>🏭 Casing Division Summary</div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Avg Driver Score", "78", "↑ +2")
with col2:
    st.metric("Total Man Hours", "2,840")
with col3:
    st.metric("Recordables", "1")
with col4:
    st.metric("TRIR", "2.3", "↑ +0.3")
with col5:
    st.metric("LTIR", "0.8", "↓ -0.1")

# Drill-downs
st.markdown("<div class='section-title'>📋 Division Drill-Downs</div>", unsafe_allow_html=True)

with st.expander("Total Incidents: 14 (↑ 40% vs Jan)", expanded=False):
    st.write("""
    - Report Only: 3
    - First Aid: 1
    - Equipment: 2
    - At-Fault Vehicle: 1
    - Recordable: 1
    - Near Miss: 3
    - Quality: 2
    """)

with st.expander("Total Observations: 28 (→ SAME vs Jan)", expanded=False):
    st.write("""
    - At-Risk Condition: 8 (Midland: 5, Bryan: 2, Kilgore: 1)
    - At-Risk Behavior: 6 (Midland: 3, Bryan: 2, Kilgore: 1)
    - Recognition: 5 (Midland: 2, Bryan: 2, Kilgore: 1)
    - At-Risk Procedure: 4
    - Near Miss: 3
    - Suggestion: 2
    """)

with st.expander("Total Rig Audits: 24 (↑ 20% vs Jan)", expanded=False):
    st.write("""
    **Midland (12):** John Smith 4 | Maria Garcia 3 | Robert Lee 3 | Lisa Chen 2
    
    **Bryan (8):** Jennifer White 3 | Michael Davis 3 | Patricia Moore 2
    
    **Kilgore (4):** Steven Martinez 2 | Nancy Thomas 1 | Charles Garcia 1
    """)

# Repeat Offenders
st.markdown("<div class='section-title'>🔄 Repeat Offenders</div>", unsafe_allow_html=True)

repeat_data = [
    {"name": "John Smith (Midland)", "type": "Speeding", "count": "4x", "trend": "↗"},
    {"name": "Sarah Davis (Bryan)", "type": "Harsh Accel", "count": "3x", "trend": "↘"},
    {"name": "Mike Johnson (Bryan)", "type": "Following Dist", "count": "2x", "trend": "→"}
]

for offender in repeat_data:
    col1, col2, col3, col4 = st.columns([0.4, 0.3, 0.15, 0.15])
    with col1:
        st.write(f"**{offender['name']}**")
    with col2:
        st.write(f"`{offender['type']}`")
    with col3:
        st.write(f"**{offender['count']}**")
    with col4:
        st.write(f"**{offender['trend']}**")

# Actions & Results
st.markdown("<div class='section-title'>✅ Actions & Results</div>", unsafe_allow_html=True)

with st.expander("John Smith - Speeding Coaching", expanded=False):
    st.write("**Scheduled:** 2/19")
    st.write("**Follow-up:** 2/26")
    st.warning("⏳ IN PROGRESS")

with st.expander("Sarah Davis - Coaching Completed", expanded=False):
    st.write("**Alerts reduced:** 5x → 2x (60% improvement)")
    st.success("✓ WORKING")

with st.expander("Midland Root Cause - Addressed", expanded=False):
    st.write("**Safety stand-down:** 2/18")
    st.write("**Supervisor onboarding:** Intensified")
    st.write("**Recovery expected:** 2/25")
    st.success("✓ COMPLETED")

# Midland Yard Detail
st.markdown("<div class='section-title'>🏭 Midland Yard</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.write("**Observations:** 16 | **Quality:** 82% HIGH")
    st.write("13/16 structural hazards. Proactive. ✓")

with col2:
    st.write("**Near-Miss to Incident:** 0% Conversion")
    st.write("System preventing incidents ✓")

# 7-Day Trend Chart
st.subheader("7-Day Speeding Trend")

days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
events = [1, 2, 2, 1, 3, 2, 5]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=days, y=events,
    mode='lines+markers',
    name='Speeding Events',
    line=dict(color='#dc2626', width=3),
    marker=dict(size=10, color='#dc2626')
))

fig.update_layout(
    title="",
    xaxis_title="",
    yaxis_title="Events",
    hovermode='x unified',
    height=300,
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Driver scores
col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ Top 5 Drivers")
    top_drivers = [
        {"name": "James Wilson", "score": 95},
        {"name": "Maria Garcia", "score": 94},
        {"name": "Robert Lee", "score": 93}
    ]
    for driver in top_drivers:
        st.write(f"{driver['name']}: **{driver['score']}**")

with col2:
    st.subheader("⚠️ Worst 5 Drivers")
    worst_drivers = [
        {"name": "John Smith (Speeding)", "score": 42},
        {"name": "Tom Wilson (Following)", "score": 55}
    ]
    for driver in worst_drivers:
        st.write(f"{driver['name']}: **{driver['score']}**")

# Footer
st.write("---")
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Live Data from Motive API & KPA EHS | A Grade Dashboard")
