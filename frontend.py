"""EmergeRoute production-oriented Streamlit frontend.

This file is a frontend layer over the existing EmergeRoute pipeline. It keeps
traffic probing, prediction, policy generation, SUMO simulation, ranking,
real-area mapping, and vehicle detection in their existing modules.

Run with:
    streamlit run frontend.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from detection_panel import render_detection_section
from map_section import render_map_section
from policy_generator import generate_candidate_policies, probe_network
from scoring_engine import rank_policies
from traffic_prediction import N_LAGS, predict_congestion_level, train_predictor
from video_upload import render_video_upload


st.set_page_config(
    page_title="EmergeRoute",
    page_icon="assets/emerge_route_favicon.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

UPLOADED_CFG = "simulation_uploaded.sumocfg"
SCENARIO_NAMES = {
    "simulation.sumocfg": "Light traffic",
    "simulation_heavy_stable.sumocfg": "Heavy congestion",
    "simulation_realistic.sumocfg": "Realistic traffic",
    "simulation_heavy.sumocfg": "Gridlock",
    UPLOADED_CFG: "Uploaded video",
}

COLORS = {
    "bg": "#090c10",
    "surface": "#11161d",
    "surface_2": "#151b23",
    "border": "#27303a",
    "text": "#f3f5f7",
    "muted": "#8d98a6",
    "green": "#39c874",
    "amber": "#e3a33d",
    "red": "#df5b5b",
    "blue": "#65aaf5",
}


st.markdown(
    f"""
<style>
:root {{
    --bg: {COLORS['bg']};
    --surface: {COLORS['surface']};
    --surface-2: {COLORS['surface_2']};
    --border: {COLORS['border']};
    --text: {COLORS['text']};
    --muted: {COLORS['muted']};
}}

.stApp {{ background: var(--bg); color: var(--text); }}
section[data-testid="stSidebar"] {{ display: none; }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ max-width: 1460px; padding: 1rem 2rem 3rem; }}

h1, h2, h3 {{ color: var(--text) !important; letter-spacing: -0.025em; }}
h1 {{ font-size: clamp(2rem, 4vw, 3.25rem) !important; font-weight: 750 !important; }}
h2 {{ font-size: 1.35rem !important; font-weight: 700 !important; margin-top: 1.8rem !important; }}
h3 {{ font-size: 1rem !important; }}
p, label {{ color: var(--text); }}

.navbar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    border-bottom: 1px solid var(--border);
    padding: 0.65rem 0 0.9rem;
    margin-bottom: 2rem;
}}
.brand {{ font-size: 1.05rem; font-weight: 800; letter-spacing: -0.015em; }}
.context {{ color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }}
.nav-links {{ display: flex; gap: 1rem; flex-wrap: wrap; }}
.nav-links span {{ color: var(--muted); font-size: 0.76rem; }}

.kicker {{
    color: {COLORS['blue']}; font-size: 0.72rem; font-weight: 750;
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.55rem;
}}
.hero-copy {{ color: var(--muted); max-width: 820px; line-height: 1.65; margin-bottom: 1.5rem; }}

.panel {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 7px; padding: 1rem 1.1rem; margin-bottom: 0.8rem;
}}
.panel-title {{ color: var(--text); font-weight: 700; font-size: 0.9rem; margin-bottom: 0.3rem; }}
.panel-copy {{ color: var(--muted); font-size: 0.8rem; line-height: 1.55; }}

.metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.65rem; margin: 0.8rem 0; }}
.metric {{ background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 0.8rem; }}
.metric-label {{ color: var(--muted); font-size: 0.67rem; text-transform: uppercase; letter-spacing: 0.07em; }}
.metric-value {{ color: var(--text); font-size: 1.35rem; font-weight: 750; margin-top: 0.2rem; font-variant-numeric: tabular-nums; }}

.status {{
    border: 1px solid var(--border); border-left: 3px solid {COLORS['blue']};
    background: var(--surface); padding: 0.65rem 0.8rem; border-radius: 5px;
    color: var(--muted); font-size: 0.82rem; line-height: 1.5; margin: 0.6rem 0;
}}
.status.ok {{ border-left-color: {COLORS['green']}; }}
.status.warn {{ border-left-color: {COLORS['amber']}; }}
.status.error {{ border-left-color: {COLORS['red']}; }}

.section-note {{ color: var(--muted); font-size: 0.8rem; line-height: 1.55; margin-bottom: 0.7rem; }}
.mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-variant-numeric: tabular-nums; }}

.stButton > button, .stDownloadButton > button {{
    border-radius: 5px !important; min-height: 2.45rem !important;
    border: 1px solid #3a4654 !important; background: var(--surface-2) !important;
    color: var(--text) !important; box-shadow: none !important; font-weight: 650 !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background: #1b232d !important; border-color: #566577 !important;
}}
.stButton > button[kind="primary"] {{
    background: #e3ebf4 !important; color: #090c10 !important; border-color: #e3ebf4 !important;
}}
.stButton > button[kind="primary"]:hover {{ background: #ffffff !important; border-color: #ffffff !important; }}

.stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {{
    background: var(--surface-2) !important; color: var(--text) !important;
    border-color: var(--border) !important; border-radius: 5px !important;
}}
div[data-testid="stExpander"] {{ background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; }}

@media (max-width: 900px) {{
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
    .navbar {{ align-items: flex-start; flex-direction: column; }}
    .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 560px) {{ .metric-grid {{ grid-template-columns: 1fr; }} }}
</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="navbar">
    <div>
        <span class="brand">EmergeRoute</span>
        <span class="context">Traffic intelligence workspace</span>
    </div>
    <div class="nav-links">
        <span>Network</span>
        <span>Detection</span>
        <span>Simulation</span>
        <span>Decision support</span>
    </div>
</div>
<div class="kicker">Traffic operations and simulation</div>
<h1>See the network. Test the intervention. Compare the outcome.</h1>
<div class="hero-copy">
    EmergeRoute combines real-area network mapping, vehicle detection, traffic-state
    probing, congestion prediction, policy generation, SUMO simulation, and
    multi-objective ranking in one analysis workspace.
</div>
""",
    unsafe_allow_html=True,
)


st.header("Real-area traffic map")
st.markdown(
    '<div class="section-note">Build or inspect the geographic network first. Map results are generated by the existing network pipeline.</div>',
    unsafe_allow_html=True,
)
render_map_section()

st.header("Policy simulation")
st.markdown(
    '<div class="section-note">Select an existing traffic scenario, optionally use the trained congestion predictor, then run the policy pipeline.</div>',
    unsafe_allow_html=True,
)

scenario_options = [
    "simulation.sumocfg",
    "simulation_heavy_stable.sumocfg",
    "simulation_realistic.sumocfg",
    "simulation_heavy.sumocfg",
]
if Path(UPLOADED_CFG).exists():
    scenario_options.append(UPLOADED_CFG)

c1, c2, c3 = st.columns([1.35, 1.35, 0.8])
with c1:
    sumocfg = st.selectbox(
        "Traffic scenario",
        scenario_options,
        format_func=lambda x: SCENARIO_NAMES.get(x, x),
    )
with c2:
    if sumocfg == UPLOADED_CFG:
        st.markdown(
            '<div class="status warn">Prediction is disabled for uploaded videos because the existing predictor is trained on the simulation scenario logs.</div>',
            unsafe_allow_html=True,
        )
        use_prediction = False
    else:
        use_prediction = st.checkbox(
            "Use XGBoost congestion prediction",
            value=True,
            help="Uses recent logged traffic history to select the congestion level.",
        )
    if not use_prediction:
        congestion_level = st.select_slider(
            "Congestion level",
            options=["low", "moderate", "high"],
            value="high",
        )
    else:
        congestion_level = None
with c3:
    st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
    run_button = st.button("Run traffic analysis", type="primary", use_container_width=True)


def metric_cards(metrics: dict) -> None:
    values = [
        ("Congestion delay", f"{metrics['avg_time_loss_s']:.0f}s"),
        ("Average travel time", f"{metrics['avg_travel_time_s']:.0f}s"),
        ("Worst-case wait", f"{metrics['max_waiting_time_s']:.0f}s"),
        ("CO2 emitted", f"{metrics['co2_kg']:.1f} kg"),
        ("Fairness gap", f"{metrics['fairness_gap_s']:.0f}s"),
        ("Trips completed", str(metrics['completed_trips'])),
        ("Safety events", str(metrics.get('safety_events', 0))),
        ("Emergency delay", f"{metrics.get('emergency_delay_s', 0):.0f}s"),
    ]
    html = '<div class="metric-grid">'
    for label, value in values:
        html += f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def prediction_for(scenario: str) -> str:
    traffic_log_map = {
        "simulation.sumocfg": "traffic_log.csv",
        "simulation_heavy.sumocfg": "traffic_log_long.csv",
        "simulation_realistic.sumocfg": "traffic_log_realistic.csv",
        "simulation_heavy_stable.sumocfg": "traffic_log_heavy.csv",
    }
    log_path = traffic_log_map.get(scenario, "traffic_log_realistic.csv")
    with st.spinner("Training congestion predictor on the selected traffic log..."):
        model, feature_cols = train_predictor(log_path)
        df = pd.read_csv(log_path).sort_values("time_s").reset_index(drop=True)
        return predict_congestion_level(model, feature_cols, df.tail(N_LAGS + 1))


if run_button:
    try:
        if use_prediction:
            congestion_level = prediction_for(sumocfg)
            st.markdown(
                f'<div class="status ok">Predicted congestion level: <b>{congestion_level.upper()}</b>. The value is derived from the selected scenario log.</div>',
                unsafe_allow_html=True,
            )

        with st.spinner("Measuring the current network state..."):
            probe = probe_network(sumocfg=sumocfg)

        busiest_tls = probe["ranked_tls"]
        candidates = generate_candidate_policies(
            busiest_tls,
            congestion_level=congestion_level,
        )

        with st.spinner(f"Testing {len(candidates)} candidate policies in SUMO..."):
            ranked = rank_policies(candidates, sumocfg=sumocfg)

        st.header("Network state")
        st.markdown(
            '<div class="section-note">These values come from the completed network probe and are not placeholders.</div>',
            unsafe_allow_html=True,
        )
        state_cols = st.columns(4)
        state_values = [
            ("Scenario", SCENARIO_NAMES.get(sumocfg, sumocfg)),
            ("Intersections", len(busiest_tls)),
            ("Peak vehicles", probe["peak_vehicles"]),
            ("Jam events", len(probe["events"])),
        ]
        for col, (label, value) in zip(state_cols, state_values):
            with col:
                st.markdown(
                    f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>',
                    unsafe_allow_html=True,
                )

        st.subheader("Highest measured queues")
        zone_cols = st.columns(min(3, max(1, len(busiest_tls[:6]))))
        max_q = max(probe["queue_totals"].values()) if probe["queue_totals"] else 1
        for i, tid in enumerate(busiest_tls[:6]):
            q = probe["queue_totals"][tid]
            if q > 0.66 * max_q:
                severity, tone = "SEVERE", COLORS["red"]
            elif q > 0.33 * max_q:
                severity, tone = "BUSY", COLORS["amber"]
            else:
                severity, tone = "NORMAL", COLORS["green"]
            with zone_cols[i % len(zone_cols)]:
                st.markdown(
                    f'<div class="panel"><div class="mono">{tid}</div><div style="font-size:1.5rem;font-weight:750;color:{tone};">{q}</div><div class="panel-copy">Accumulated queue · {severity}</div></div>',
                    unsafe_allow_html=True,
                )

        st.header("Recommended policy")
        top = ranked[0]
        baseline = next((e for e in ranked if e["policy_name"].lower().startswith("baseline")), None)
        st.markdown(f"### {top['policy_name']}")
        st.markdown(
            f'<div class="panel"><div class="panel-title">Why this policy was selected</div><div class="panel-copy">{top["explanation"]}</div></div>',
            unsafe_allow_html=True,
        )
        metric_cards(top["metrics"])

        if baseline is not None and baseline is not top:
            bm = baseline["metrics"]
            comparison = []
            for label, key, unit, lower_better in [
                ("Congestion delay", "avg_time_loss_s", "s", True),
                ("Average travel time", "avg_travel_time_s", "s", True),
                ("Worst-case wait", "max_waiting_time_s", "s", True),
                ("CO2 emitted", "co2_kg", "kg", True),
                ("Fairness gap", "fairness_gap_s", "s", True),
                ("Trips completed", "completed_trips", "", False),
                ("Safety events", "safety_events", "", True),
                ("Emergency delay", "emergency_delay_s", "s", True),
            ]:
                b, r = bm.get(key, 0), top["metrics"].get(key, 0)
                d = r - b
                comparison.append({"Metric": label, "Baseline": b, "Recommended": r, "Change": d})
            comparison_df = pd.DataFrame(comparison)
            st.subheader("Recommended policy vs baseline")
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        st.header("Policy comparison")
        chart_df = pd.DataFrame(
            [
                {
                    "Policy": f"#{entry['rank']} {entry['policy_name']}",
                    "Congestion delay (s)": entry["metrics"]["avg_time_loss_s"],
                    "Average travel time (s)": entry["metrics"]["avg_travel_time_s"],
                    "CO2 (kg)": entry["metrics"]["co2_kg"],
                }
                for entry in ranked
            ]
        )
        st.plotly_chart(
            px.bar(
                chart_df,
                x="Policy",
                y=["Congestion delay (s)", "Average travel time (s)", "CO2 (kg)"],
                barmode="group",
            ),
            use_container_width=True,
        )

        st.header("Candidate policies")
        for entry in ranked:
            label = f"#{entry['rank']} {entry['policy_name']}"
            if entry["pareto_optimal"]:
                label += " · Pareto-optimal"
            with st.expander(label):
                st.write(entry["explanation"])
                metric_cards(entry["metrics"])

        if probe["events"]:
            st.header("Traffic events")
            for event in probe["events"][:10]:
                st.markdown(
                    f'<div class="status warn">Vehicle <b>{event["vehicle_id"]}</b> was teleported after waiting too long at t={event["time_s"]}s.</div>',
                    unsafe_allow_html=True,
                )

    except Exception as exc:
        st.markdown(
            f'<div class="status error"><b>Analysis could not be completed.</b><br>{exc}</div>',
            unsafe_allow_html=True,
        )

st.header("Vehicle detection")
st.markdown(
    '<div class="section-note">Upload a traffic video to use the existing vehicle-detection pipeline. Detection output remains separate from simulated policy results.</div>',
    unsafe_allow_html=True,
)
render_video_upload()
render_detection_section()

st.markdown(
    '<div class="panel"><div class="panel-title">Operational scope</div><div class="panel-copy">EmergeRoute provides decision support from the existing SUMO and detection pipelines. Recommendations are not automatically applied to real traffic signals.</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="panel-copy">EmergeRoute · <a href="https://github.com/meryl25bai10663-coder/YDFNet_Vehicle_Detection" target="_blank">Project repository</a> · Privacy Policy · Terms & Conditions</div>',
    unsafe_allow_html=True,
)
