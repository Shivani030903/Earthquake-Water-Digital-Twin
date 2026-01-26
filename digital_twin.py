import networkx as nx
import pandas as pd

def create_digital_twin():
    G = nx.Graph()

    nodes = pd.read_csv("data/nodes.csv")
    pipes = pd.read_csv("data/pipes.csv")

    # -------------------------
    # ADD NODES
    # -------------------------

    for _, n in nodes.iterrows():
        G.add_node(
    n['node_id'],
    pos=(n['lon'], n['lat']),
    lat=n['lat'],
    lon=n['lon'],
    priority=n['priority'],
    type=n['type'],
    demand=n['demand']
)

    # -------------------------
    # ADD PIPES (WITH is_physical)
    # -------------------------

    for _, p in pipes.iterrows():
        G.add_edge(
            p['from'], p['to'],
            pipe_id=p['pipe_id'],
            length=p['length'],
            material=p['material'],
            age=p['age'],
            soil=p['soil'],
            pressure_cap=p['pressure_cap'],
            status="healthy",
            is_physical=bool(p.get("is_physical", 1)) #to show real pipes

        )

    return G