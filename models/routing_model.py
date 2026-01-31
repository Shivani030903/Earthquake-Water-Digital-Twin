import networkx as nx

def edge_weight(G, u, v):
    edge = G.edges[u, v]
    return (
        edge['length']
        + 50 * edge.get('risk', 0)
        - 20 * G.nodes[v]['priority']
    )

def compute_routes(G, source, targets):
    routes = {}
    for t in targets:
        try:
            routes[t] = nx.shortest_path(
                G,
                source=source,
                target=t,
                weight=lambda u, v, d: edge_weight(G, u, v)
            )
        except nx.NetworkXNoPath:
            routes[t] = None
    return routes

def remove_failed_pipes(G):
    """
    Removes all pipes marked as failed from the graph
    """
    failed_edges = [
        (u, v) for u, v, d in G.edges(data=True)
        if d.get("status") == "failed"
    ]
    G.remove_edges_from(failed_edges)
    return G

# ------------------------------
# ADD REROUTED (LOGICAL) EDGES
# ------------------------------
def add_rerouted_pipe(G, u, v, length, failure_prob=0.1):
    G.add_edge(
        u, v,
        status="rerouted",
        is_physical=False,
        failure_prob=failure_prob,
        length=length
    )
    return G


def mark_supply_status(G, source="N1"):
    for n in G.nodes:
        G.nodes[n]["supplied"] = nx.has_path(G, source, n)
    return G

