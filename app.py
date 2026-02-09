import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="BRHAS Safety Dashboard",
    page_icon="🏭",
    layout="wide",
)

# Header
st.title("🏭 BRHAS Safety Dashboard")
st.caption("Casing Division | Live Safety Intelligence")
st.divider()

# --- KPI Targets vs Actual ---
st.subheader("📊 KPI Targets vs Actual")
col1, col2, col3, col4 = st.columns(4)
col1.metric("TRIR", "2.3", "0.3", delta_color="inverse")
col2.metric("LTIR", "0.8", "-0.1")
col3.metric("Avg Driver Score", "78", "+2")
col4.metric("Observations", "28", "0")

# --- Financial Impact ---
st.subheader("💰 Financial Impact")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Workers' Comp", "$48.5K", "5 claims")
col2.metric("Lost Productivity", "$22.3K", "182 hrs lost")
col3.metric("Regulatory Risk", "$15K", "OSHA exposure")
col4.metric("Total Feb Cost", "$85.8K")

# --- Predictive Alert ---
st.subheader("⚡ Predictive Alert")
st.warning(
    "**Midland Trend: +40% vs Jan** — If trend continues: 12-14 incidents by month-end. "
    "Root cause: supervisor transition (44%), weather (33%), equipment (22%). "
    "Confidence: 75%. "
    "Action: Safety stand-down 2/18, supervisor coaching, daily briefings."
)

# --- Casing Division Summary ---
st.subheader("🏭 Casing Division Summary")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Avg Driver Score", "78", "↑ +2")
col2.metric("Total Man Hours", "2,840")
col3.metric("Recordables", "1")
col4.metric("TRIR", "2.3", "↑ +0.3")
col5.metric("LTIR", "0.8", "↓ -0.1")

# --- Drill-Downs ---
st.subheader("📋 Division Drill-Downs")

with st.expander("Total Incidents: 14 (↑ 40% vs Jan)"):
    st.markdown(
        "- Report Only: 3\n- First Aid: 1\n- Equipment: 2\n"
        "- At-Fault Vehicle: 1\n- Recordable: 1\n- Near Miss: 3\n- Quality: 2"
    )

with st.expander("Total Observations: 28 (→ SAME vs Jan)"):
    st.markdown(
        "- At-Risk Condition: 8 (Midland 5, Bryan 2, Kilgore 1)\n"
        "- At-Risk Behavior: 6 (Midland 3, Bryan 2, Kilgore 1)\n"
        "- Recognition: 5\n- At-Risk Procedure: 4\n- Near Miss: 3\n- Suggestion: 2"
    )

with st.expander("Total Rig Audits: 24 (↑ 20% vs Jan)"):
    st.markdown(
        "**Midland (12):** John Smith 4 | Maria Garcia 3 | Robert Lee 3 | Lisa Chen 2\n\n"
        "**Bryan (8):** Jennifer White 3 | Michael Davis 3 | Patricia Moore 2\n\n"
        "**Kilgore (4):** Steven Martinez 2 | Nancy Thomas 1 | Charles Garcia 1"
    )

# --- Repeat Offenders ---
st.subheader("🔄 Repeat Offenders")
for name, violation, count, trend in [
    ("John Smith (Midland)", "Speeding", "4x", "↗"),
    ("Sarah Davis (Bryan)", "Harsh Accel", "3x", "↘"),
    ("Mike Johnson (Bryan)", "Following Dist", "2x", "→"),
]:
    c1, c2, c3, c4 = st.columns([0.4, 0.3, 0.15, 0.15])
    c1.write(f"**{name}**")
    c2.write(f"`{violation}`")
    c3.write(f"**{count}**")
    c4.write(f"**{trend}**")

# --- Actions & Results ---
st.subheader("✅ Actions & Results")

with st.expander("John Smith — Speeding Coaching"):
    st.write("**Scheduled:** 2/19 | **Follow-up:** 2/26")
    st.warning("⏳ IN PROGRESS")

with st.expander("Sarah Davis — Coaching Completed"):
    st.write("Alerts reduced: 5x → 2x (60% improvement)")
    st.success("✓ WORKING")

with st.expander("Midland Root Cause — Addressed"):
    st.write("Safety stand-down: 2/18 | Supervisor onboarding intensified | Recovery expected: 2/25")
    st.success("✓ COMPLETED")

# --- 7-Day Speeding Trend ---
st.subheader("📈 7-Day Speeding Trend")

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
events = [1, 2, 2, 1, 3, 2, 5]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=days, y=events,
    mode="lines+markers",
    line=dict(color="#dc2626", width=3),
    marker=dict(size=10, color="#dc2626"),
))
fig.update_layout(
    yaxis_title="Events",
    hovermode="x unified",
    height=300,
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True)

# --- Driver Scores ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ Top Drivers")
    for name, score in [("James Wilson", 95), ("Maria Garcia", 94), ("Robert Lee", 93)]:
        st.write(f"{name}: **{score}**")

with col2:
    st.subheader("⚠️ Needs Improvement")
    for name, score in [("John Smith (Speeding)", 42), ("Tom Wilson (Following)", 55)]:
        st.write(f"{name}: **{score}**")

# Footer
st.divider()
st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | BRHAS Safety Dashboard")
