import networkx as nx

def allocate_water(G, total_supply, source="N1"):
    reachable = [
        n for n in G.nodes
        if nx.has_path(G, source, n)
    ]

    if not reachable:
        # No reachable nodes → no allocation
        return {}

    weighted_demand = sum(
        G.nodes[n].get('demand', 0) * G.nodes[n].get('priority', 0)
        for n in reachable
    )

    allocation = {}

    if weighted_demand == 0:
        # Avoid division by zero
        # Option 1: allocate zero to everyone
        for n in reachable:
            allocation[n] = 0
        return allocation

        # Option 2 (alternative): equal split
        # equal_share = total_supply / len(reachable)
        # return {n: equal_share for n in reachable}

    for n in reachable:
        allocation[n] = (
            total_supply *
            (G.nodes[n].get('demand', 0) * G.nodes[n].get('priority', 0)) /
            weighted_demand
        )

    return allocation
