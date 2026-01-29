import networkx as nx
from models.routing_model import add_rerouted_pipe

def auto_reroute(G, source="N1"):
    """
    Automatically adds logical reroute edges
    for disconnected critical nodes
    """

    # -------------------------------------------------
    # STEP 1: Find nodes still connected to the source
    # -------------------------------------------------
    reachable = {
        n for n in G.nodes
        if nx.has_path(G, source, n)
    }

    # -------------------------------------------------
    # STEP 2: Find critical nodes that lost connectivity
    # -------------------------------------------------
    critical_lost = [
        n for n, d in G.nodes(data=True)
        if d.get("priority", 0) >= 4 and n not in reachable
    ]

    # -------------------------------------------------
    # STEP 3: Try to reroute each lost critical node
    # -------------------------------------------------
    for critical in critical_lost:

        for donor in reachable:

            # Skip source itself
            if donor == source:
                continue

            # Avoid useless reroutes
            if nx.has_path(G, donor, critical):
                continue

            # -------------------------------------------------
            # STEP 4: Add logical reroute edge
            # -------------------------------------------------
            add_rerouted_pipe(G, donor, critical)

            # Only one reroute per critical node
            break

    return G
