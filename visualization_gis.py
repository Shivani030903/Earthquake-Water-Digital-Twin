import plotly.graph_objects as go

def plot_gis_network(G):
    lats = []
    lons = []

    for n, d in G.nodes(data=True):
        lat = d.get("lat")
        lon = d.get("lon")

        if lat is not None and lon is not None:
            lats.append(lat)
            lons.append(lon)

    # SAFETY CHECK
    if len(lats) == 0:
        raise ValueError("No GIS coordinates found in graph nodes")

    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    fig = go.Figure()

    # ----------------------
    # DRAW PIPES
    # ----------------------
    for u, v, d in G.edges(data=True):
        if (
            G.nodes[u].get("lat") is None or
            G.nodes[u].get("lon") is None or
            G.nodes[v].get("lat") is None or
            G.nodes[v].get("lon") is None
        ):
            continue

        color = "red" if d.get("status") == "failed" else "blue"

        fig.add_trace(go.Scattermapbox(
            lat=[G.nodes[u]["lat"], G.nodes[v]["lat"]],
            lon=[G.nodes[u]["lon"], G.nodes[v]["lon"]],
            mode="lines",
            line=dict(width=4, color=color),
            hoverinfo="text",
            text=f"Failure Prob: {round(d.get('failure_prob', 0), 2)}"
        ))

    # ----------------------
    # DRAW NODES
    # ----------------------
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode="markers",
        marker=dict(size=10, color="red"),
        hoverinfo="none"
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=14
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig