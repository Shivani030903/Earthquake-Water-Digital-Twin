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