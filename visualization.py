import plotly.graph_objects as go

# ==================================================
# WATER NETWORK VISUALIZATION
# ==================================================
def plot_water_network(G, title="Water Network"):
    fig = go.Figure()

    # -------------------
    # Draw Pipes (Edges)
    # -------------------
    for u, v, d in G.edges(data=True):
        x0, y0 = G.nodes[u]['pos']
        x1, y1 = G.nodes[v]['pos']

        color = 'red' if d.get('status') == 'failed' else 'gray'

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=4, color=color),
            hoverinfo='text',
            text=(
                f"Pipe ID: {d.get('pipe_id', 'N/A')}<br>"
                f"Status: {d.get('status', 'unknown')}<br>"
                f"Failure Prob: {round(d.get('failure_prob', 0), 2)}"
            ),
            showlegend=False
        ))

    # -------------------
    # Draw Nodes
    # -------------------
    node_x, node_y, node_text, node_color = [], [], [], []

    for n, d in G.nodes(data=True):
        x, y = d['pos']
        node_x.append(x)
        node_y.append(y)
        node_text.append(
            f"Node: {n}<br>"
            f"Type: {d.get('type')}<br>"
            f"Priority: {d.get('priority')}"
        )
        node_color.append(d.get('priority', 1))

    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[n for n in G.nodes()],
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=16,
            color=node_color,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Node Priority"),
            line=dict(width=1, color='black')
        ),
        showlegend=False
    ))

    # -------------------
    # Layout
    # -------------------
    fig.update_layout(
        title=title,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


# ==================================================
# FAILURE PROBABILITY HEATMAP
# ==================================================
def plot_failure_heatmap(G):
    x, y, prob = [], [], []

    for u, v, d in G.edges(data=True):
        x.append(G.nodes[u]['pos'][0])
        y.append(G.nodes[u]['pos'][1])
        prob.append(d.get('failure_prob', 0))

    fig = go.Figure(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=20,
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
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig