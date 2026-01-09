import streamlit as st
import time

from digital_twin import create_digital_twin
from models.seismic_model import seismic_stress
from models.risk_model import compute_risk
from models.routing_model import compute_routes
from models.allocation_model import allocate_water
from models.time_simulation import temporal_stress
from models.ml_failure_model import predict_failure_probability

from visualization import plot_water_network, plot_failure_heatmap
from visualization_gis import plot_gis_network
from metrics import compute_metrics
from export import export_results

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(layout="wide")
st.title("🌍 Earthquake-Aware Water Distribution Digital Twin")

# ---------------------------
# SESSION STATE (MUST BE FIRST)
# ---------------------------
if "time" not in st.session_state:
    st.session_state.time = 0

if "playing" not in st.session_state:
    st.session_state.playing = False

# ---------------------------
# PLAY / PAUSE CONTROLS
# ---------------------------
colA, colB = st.columns(2)

with colA:
    if st.button("▶ Play"):
        st.session_state.playing = True

with colB:
    if st.button("⏸ Pause"):
        st.session_state.playing = False

if st.session_state.playing:
    st.session_state.time += 1
    if st.session_state.time > 10:
        st.session_state.time = 10
    time.sleep(0.8)
    st.rerun()

# ---------------------------
# USER INPUT
# ---------------------------
magnitude = st.slider("Earthquake Magnitude", 4.0, 8.0, 6.5)
time_step = st.slider("Simulation Time (minutes)", 0, 10, st.session_state.time)

# ---------------------------
# CREATE DIGITAL TWIN
# ---------------------------
G_before = create_digital_twin()
G_after = G_before.copy()

# ---------------------------
# ML FEATURE MAPS
# ---------------------------
material_score = {
    "CI": 0.8,
    "DI": 0.5,
    "PVC": 0.3
}

soil_score = {
    "clay": 0.7,
    "sand": 0.8,
    "silt": 0.75,
    "rock": 0.3
}

# ---------------------------
# EARTHQUAKE + ML FAILURE PROBABILITY
# ---------------------------
for u, v, data in G_after.edges(data=True):
    base_stress = seismic_stress(magnitude, 5, data['soil'])
    stress = temporal_stress(base_stress, time_step)

    failure_prob = predict_failure_probability(
        stress,
        data['age'],
        material_score.get(data['material'], 0.6),
        soil_score.get(data['soil'], 0.4)
    )

    data['stress'] = stress
    data['failure_prob'] = failure_prob
    data['status'] = 'failed' if failure_prob > 0.6 else 'healthy'

# ---------------------------
# REMOVE FAILED PIPES
# ---------------------------
failed_edges = [(u, v) for u, v, d in G_after.edges(data=True) if d['status'] == 'failed']
G_after.remove_edges_from(failed_edges)

# ---------------------------
# CRITICAL NODES
# ---------------------------
critical_nodes = [n for n in G_after.nodes if G_after.nodes[n]['priority'] >= 4]

# ---------------------------
# ROUTING + WATER ALLOCATION
# ---------------------------
routes = compute_routes(G_after, "N1", critical_nodes)
allocation = allocate_water(G_after, 500)

# ---------------------------
# METRICS
# ---------------------------
metrics = compute_metrics(G_before, G_after, critical_nodes)

# ---------------------------
# NETWORK VISUALIZATION
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Before Earthquake")
    st.plotly_chart(plot_water_network(G_before), use_container_width=True)

with col2:
    st.subheader("After Earthquake & Rerouting")
    st.plotly_chart(plot_water_network(G_after), use_container_width=True)

# ---------------------------
# GIS MAP
# ---------------------------
st.subheader("🗺️ GIS-Based Water Network")
st.plotly_chart(plot_gis_network(G_after), use_container_width=True)

# ---------------------------
# FAILURE HEATMAP
# ---------------------------
st.subheader("🔥 Failure Probability Heatmap")
st.plotly_chart(plot_failure_heatmap(G_after), use_container_width=True)

# ---------------------------
# ROUTES
# ---------------------------
st.subheader("🚑 Critical Supply Routes")
for node, path in routes.items():
    if path:
        st.success(f"{node}: {' → '.join(path)}")
    else:
        st.error(f"{node}: No available route")

# ---------------------------
# METRICS DISPLAY
# ---------------------------
st.subheader("📊 System Performance Metrics")

m1, m2, m3 = st.columns(3)
m1.metric("Failed Pipes", metrics["failed_pipes"])
m2.metric("Critical Nodes Served (%)", metrics["service_ratio"])
m3.metric("Connectivity Loss (%)", metrics["connectivity_loss"])

# ---------------------------
# EXPORT
# ---------------------------
if st.button("📤 Export Results"):
    df = export_results(G_after)
    st.success("Results exported!")
    st.dataframe(df)