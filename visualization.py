import plotly.graph_objects as go
import networkx as nx

# ==================================================
# WATER NETWORK VISUALIZATION
# ==================================================
def plot_water_network(G, pos, title="Water Network"):
    fig = go.Figure()

    

    # -------------------
    # Draw Pipes (Edges)
    # -------------------
    for u, v, d in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        if d.get("status") == "failed":
            color = "red"
            width = 4
            dash = "dot"
        elif d.get("status") == "rerouted":
            color = "green"
            width = 3
            dash = "dash"
        else:
            color = "gray"
            width = 1
            dash = "solid"


        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=width, color=color, dash=dash),
            hoverinfo='text',
            text=(
                f"Pipe ID: {d.get('pipe_id', 'N/A')}<br>"
                f"Status: {d.get('status', 'unknown')}<br>"
                f"Failure Prob: {round(d.get('failure_prob', 0), 2)}"
            ),
            showlegend=False
        ))

    # -------------------
    # Draw Nodes (Hierarchy)
    # -------------------
    node_x, node_y = [], []
    node_size, node_color = [], []
    node_labels, node_hover = [], []



    for n, d in G.nodes(data=True):
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)

        if n == "N1":
            node_size.append(40)
            node_color.append("blue")
            label = "N1 (Source)"

        elif d.get("priority", 0) >= 4:
            node_size.append(28)
            node_color.append("red")
            label = n

        else:
            node_size.append(18)
            node_color.append("lightgray")
            label = n

        node_labels.append(label)

        node_hover.append(
            f"Node: {n}<br>"
            f"Type: {d.get('type')}<br>"
            f"Priority: {d.get('priority')}"
        )

    # ADD NODES TRACE (ONLY ONCE)
    fig.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    text=node_labels,          # ✅ visible labels
    textposition="top center",
    textfont=dict(
        size=12,
        color="black"
    ),
    hoverinfo='text',
    hovertext=node_hover,      # ✅ hover info
    marker=dict(
        size=node_size,
        color=node_color,
        line=dict(width=1, color='black')
    ),
    showlegend=False
))


    # -------------------
    # Layout
    # -------------------
    fig.update_layout(
    title=title,
    margin=dict(l=5, r=5, t=40, b=5),
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    plot_bgcolor="white"
)

    return fig


# ==================================================
# FAILURE PROBABILITY HEATMAP
# ==================================================
def plot_failure_heatmap(G):
    pos = nx.spring_layout(G, seed=42)

    x, y, prob = [], [], []

    for u, v, d in G.edges(data=True):
        x.append(pos[u][0])
        y.append(pos[u][1])
        prob.append(d.get('failure_prob', 0))

    fig = go.Figure(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=18,
            color=prob,
            colorscale='Hot',
            showscale=True,
            colorbar=dict(title="Failure Probability"),
            opacity=0.85
        ),
        hoverinfo='text',
        text=[f"P(failure)={round(p,2)}" for p in prob]
    ))

    fig.update_layout(
        title="Pipe Failure Probability Heatmap",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white'
    )

    return fig
