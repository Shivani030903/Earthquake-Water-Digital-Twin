import networkx as nx
from models.routing_model import add_rerouted_pipe

MAX_REROUTE_DISTANCE = 800
MIN_PRESSURE_REQUIRED = 80  # kept for future extension

def auto_reroute(G, source="N1"):
    """
    Automatically reroutes water to disconnected critical nodes
    using shortest available safe paths.
    """

    # ------------------------------------
    # STEP 1: Nodes still connected to source
    # ------------------------------------
    reachable = {
        n for n in G.nodes
        if nx.has_path(G, source, n)
    }

    # ------------------------------------
    # STEP 2: Critical nodes that lost supply
    # ------------------------------------
    critical_lost = [
        n for n, d in G.nodes(data=True)
        if d.get("priority", 0) >= 4 and n not in reachable
    ]

    # ------------------------------------
    # STEP 3: Reroute each lost critical node
    # ------------------------------------
    for critical in critical_lost:
        best_donor = None
        best_distance = float("inf")

        for donor in reachable:

            if donor == source:
                continue

            try:
                dist = nx.shortest_path_length(
                    G, donor, critical, weight="length"
                )
            except nx.NetworkXNoPath:
                continue

            if dist <= MAX_REROUTE_DISTANCE and dist < best_distance:
                best_distance = dist
                best_donor = donor

        # ------------------------------------
        # STEP 4: Add logical rerouted pipe
        # ------------------------------------
        if best_donor:
            add_rerouted_pipe(
                G,
                best_donor,
                critical,
                length=best_distance,
                failure_prob=0.1
            )

    return G
