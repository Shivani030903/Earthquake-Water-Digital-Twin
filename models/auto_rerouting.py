import networkx as nx
from models.routing_model import add_rerouted_pipe

MAX_REROUTE_DISTANCE = 800
MIN_PRESSURE_REQUIRED = 80
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
            # STEP 4: Add logical reroute edge (Rerouting distance is computed along existing pipes instead of direct node jumps.)
            # -------------------------------------------------
            try:
                dist = nx.shortest_path_length(
                    G,
                    donor,
                    critical,
                    weight="length"
                )
            except nx.NetworkXNoPath:
                continue

            # Reject long-distance reroutes
            if dist > MAX_REROUTE_DISTANCE:
                continue

            path = nx.shortest_path(G, donor, critical, weight="length")

            min_pressure = min(
                G.edges[path[i], path[i + 1]].get("pressure_cap", 0)
                for i in range(len(path) - 1)
            )

            if min_pressure < MIN_PRESSURE_REQUIRED:
                continue

            # -------------------------------------------------
            # ✅ STEP 6: ADD REROUTED PIPE 
            # -------------------------------------------------
            add_rerouted_pipe(
                G,
                donor,
                critical,
                length=dist,
                failure_prob=0.1
            )


            # Only one reroute per critical node
            break

    return G
