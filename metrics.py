import networkx as nx

def compute_metrics(G_before, G_after, critical_nodes=None):
    """
    Computes detailed metrics for water network performance.
    
    Parameters:
        G_before: networkx.Graph
            The graph before failures.
        G_after: networkx.Graph
            The graph after failures.
        critical_nodes: list (optional)
            List of nodes considered "critical".
    
    Returns:
        dict of metrics
    """
    # -----------------------------
    # Identify node categories
    # -----------------------------
    if critical_nodes is None:
        critical_nodes = [n for n, d in G_before.nodes(data=True) if d.get('priority', 0) >= 4]
    
    normal_nodes = [n for n in G_before.nodes if n not in critical_nodes]

    # -----------------------------
    # Failed pipes
    # -----------------------------
    failed_pipes = sum(
    1 for _, _, d in G_after.edges(data=True)
    if d.get("status") == "failed"
)


    # -----------------------------
    # Critical node connectivity
    # -----------------------------
    critical_served = sum(1 for n in critical_nodes if nx.has_path(G_after, "N1", n))
    critical_service_ratio = (critical_served / len(critical_nodes)) * 100
    critical_connectivity_loss = ((len(critical_nodes) - critical_served) / len(critical_nodes)) * 100

    # -----------------------------
    # Normal node connectivity
    # -----------------------------
    normal_served = sum(1 for n in normal_nodes if nx.has_path(G_after, "N1", n))
    normal_service_ratio = (normal_served / len(normal_nodes)) * 100 if normal_nodes else 0
    normal_connectivity_loss = ((len(normal_nodes) - normal_served) / len(normal_nodes)) * 100 if normal_nodes else 0

    # -----------------------------
    # Overall connectivity (all nodes)
    # -----------------------------
    all_nodes = critical_nodes + normal_nodes
    all_served = critical_served + normal_served
    overall_service_ratio = (all_served / len(all_nodes)) * 100
    overall_connectivity_loss = ((len(all_nodes) - all_served) / len(all_nodes)) * 100

    # -----------------------------
    # Return metrics
    # -----------------------------
    return {
        "failed_pipes": failed_pipes,
        "critical_nodes_served": critical_served,
        "critical_service_ratio": round(critical_service_ratio, 2),
        "critical_connectivity_loss": round(critical_connectivity_loss, 2),
        "normal_nodes_served": normal_served,
        "normal_service_ratio": round(normal_service_ratio, 2),
        "normal_connectivity_loss": round(normal_connectivity_loss, 2),
        "overall_service_ratio": round(overall_service_ratio, 2),
        "overall_connectivity_loss": round(overall_connectivity_loss, 2),
        "total_critical_nodes": len(critical_nodes),
        "total_normal_nodes": len(normal_nodes),
        "baseline_service": 40  # optional: baseline for comparison
    }
