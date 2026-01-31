import streamlit as st
import time
import numpy as np

MAX_REROUTE_DISTANCE = 800  # meters (emergency operational limit)
MIN_PRESSURE_REQUIRED = 80 # minimum safe pressure

# ---------------------------
# FAILURE CONTROL (FOR DEMO)
# ---------------------------
#FAILURE_THRESHOLD = 0.35

from digital_twin import create_digital_twin
from models.network_generator import generate_network
from models.seismic_model import seismic_stress
#from models.risk_model import compute_risk
from models.routing_model import compute_routes
from models.allocation_model import allocate_water
from models.auto_rerouting import auto_reroute
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

# ===========================
# 🔹 SIDEBAR — NETWORK CONFIG
# ===========================
st.sidebar.header("🛠 Network Configuration")

network_mode = st.sidebar.radio(
    "Network Source",
    ["Manual (CSV)", "Auto-Generated"]
)

if network_mode == "Auto-Generated":
    n_nodes = st.sidebar.slider("Number of Nodes", 10, 100, 25)

    if st.sidebar.button("Generate Network"):
        n_nodes_created, n_pipes_created = generate_network(n_nodes)
        st.sidebar.success(
            f"Generated {n_nodes_created} nodes & {n_pipes_created} pipes"
        )

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

# ---------------------------------
# GEO-BASED NODE POSITIONS (lat/lon)
# ---------------------------------
fixed_pos = {
    n: (d.get("lon"), d.get("lat"))
    for n, d in G_before.nodes(data=True)
    if d.get("lon") is not None and d.get("lat") is not None
}


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


#  VERY IMPORTANT GUARD
if time_step == 0:
    # No earthquake effects at time 0
    G_after = G_before.copy()
    G_operational = G_before.copy()
    
else:
    # Earthquake effects start only after time > 0
    G_after = G_before.copy()

    for u, v, data in G_after.edges(data=True):
        distance = data.get("length", np.random.uniform(50, 200)) / 100
        base_stress = seismic_stress(magnitude, distance, data['soil'])
        stress = temporal_stress(base_stress, time_step)

        failure_prob = predict_failure_probability(
            stress,
            data['age'],
            material_score.get(data['material'], 0.6),
            soil_score.get(data['soil'], 0.4)
        )

        # ---------------------------------
        # BACKBONE PIPE PROTECTION
        # ---------------------------------
        if data.get("pressure_cap", 0) > 100:
            failure_prob *= 0.85

        # Time-based progressive damage
        failure_prob = min(
            1.0,
            failure_prob * (1 + 0.05 * time_step)
        )

        # ---------------------------------
        # SAFETY CLAMP (VERY IMPORTANT)
        # ---------------------------------
        failure_prob = max(0.05, min(1.0, failure_prob))

        data['stress'] = stress
        data['failure_prob'] = failure_prob

        # ---------------------------------
        # DYNAMIC FAILURE THRESHOLD (Finds the top 30% most risky)
        # ---------------------------------
        
    all_failure_probs = [
        d["failure_prob"]
        for _, _, d in G_after.edges(data=True)
    ]

    if all_failure_probs:
        raw_threshold = np.percentile(all_failure_probs, 70)

        # ---- SAFETY CLAMP ----
        FAILURE_THRESHOLD = min(raw_threshold, 0.65)
    else:
        FAILURE_THRESHOLD = 0.6
   
    
    st.write(f"🔴 Dynamic Failure Threshold: {FAILURE_THRESHOLD:.2f}")


    for u, v, data in G_after.edges(data=True):
        data["status"] = (
            "failed"
            if data["failure_prob"] > FAILURE_THRESHOLD
            else "healthy"
        )

    # Remove failed pipes ONLY after time > 0
    G_operational = G_after.copy()
    failed_edges = [
        (u, v)
        for u, v, d in G_after.edges(data=True)
        if d['status'] == 'failed'
    ]
    G_operational.remove_edges_from(failed_edges)

    # Automatic rerouting
    G_operational = auto_reroute(G_operational)

    # Copy rerouted edges back for display
    for u, v, d in G_operational.edges(data=True):
        if d.get("status") == "rerouted":
            G_after.add_edge(
                u, v,
                length=d.get("length", 100),
                material=d.get("material", "PVC"),
                soil=d.get("soil", "sand"),
                age=0,
                status="rerouted"
            )


    # DO NOT REMOVE FAILED NODES
    for u, v in failed_edges:
        G_after.edges[u, v]["status"] = "failed"

# ---------------------------
# CRITICAL NODES
# ---------------------------
critical_nodes = [
    n for n in G_operational.nodes
    if G_operational.nodes[n].get('priority', 0) >= 4
]

# ---------------------------
# ROUTING + WATER ALLOCATION
# ---------------------------
routes = compute_routes(G_operational, "N1", critical_nodes)
allocation = allocate_water(G_operational, 500)

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
    st.plotly_chart(
    plot_water_network(G_before, fixed_pos, title="Before Earthquake"),
    use_container_width=True
)
with col2:
    st.subheader("After Earthquake & Rerouting")
    st.plotly_chart(
    plot_water_network(G_after, fixed_pos, title="After Earthquake & Rerouting"),
    use_container_width=True
)

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
m2.metric("Critical Nodes Served (%)", metrics["critical_service_ratio"])
m3.metric("Connectivity Loss (%)", metrics["critical_connectivity_loss"])

# ---------------------------
# EXPORT
# ---------------------------
if st.button("📤 Export Results"):
    df = export_results(G_after)
    st.success("Results exported!")
    st.dataframe(df)