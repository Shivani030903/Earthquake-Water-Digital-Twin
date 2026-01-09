def allocate_water(G, total_supply):
    weighted_demand = sum(
        G.nodes[n]['demand'] * G.nodes[n]['priority']
        for n in G.nodes
    )

    allocation = {}
    for n in G.nodes:
        allocation[n] = (
            total_supply *
            (G.nodes[n]['demand'] * G.nodes[n]['priority']) /
            weighted_demand
        )

    return allocation