import networkx as nx

def compute_metrics(G_before, G_after, critical_nodes):
    failed_pipes = len(G_before.edges) - len(G_after.edges)

    served = 0
    for node in critical_nodes:
        if nx.has_path(G_after, "N1", node):
            served += 1

    service_ratio = (served / len(critical_nodes)) * 100

    connectivity_loss = (
        (nx.number_connected_components(G_after) -
         nx.number_connected_components(G_before))
        / nx.number_connected_components(G_before)
    ) * 100

    return {
        "failed_pipes": failed_pipes,
        "service_ratio": round(service_ratio, 2),
        "connectivity_loss": round(max(connectivity_loss, 0), 2),
        "baseline_service": 40  # assumed no-rerouting baseline
    }