import random
import pandas as pd


def generate_network(
    n_nodes=25,
    center_lat=23.26,
    center_lon=77.41,
    radius=0.01
):
    nodes = []
    pipes = []

    # -----------------------
    # CREATE NODES
    # -----------------------
    for i in range(1, n_nodes + 1):
        node_type = "critical" if i <= 3 else "residential"

        nodes.append({
            "node_id": f"N{i}",
            "type": node_type,
            "demand": random.randint(40, 150),
            "priority": random.randint(4, 5) if node_type == "critical" else random.randint(1, 3),
            "lat": center_lat + random.uniform(-radius, radius),
            "lon": center_lon + random.uniform(-radius, radius)
        })

    # -----------------------
    # CREATE PIPES
    # -----------------------
    for i in range(2, n_nodes + 1):
        pipes.append({
            "pipe_id": f"P{i}",
            "from": f"N{random.randint(1, i - 1)}",
            "to": f"N{i}",
            "length": random.randint(200, 800),
            "material": random.choice(["CI", "DI", "PVC"]),
            "age": random.randint(5, 50),
            "soil": random.choice(["rock", "clay", "sand"]),
            "pressure_cap": random.randint(70, 130)
        })

    # -----------------------
    # SAVE TO CSV (IMPORTANT)
    # -----------------------
    pd.DataFrame(nodes).to_csv("data/nodes.csv", index=False)
    pd.DataFrame(pipes).to_csv("data/pipes.csv", index=False)

    return len(nodes), len(pipes)
