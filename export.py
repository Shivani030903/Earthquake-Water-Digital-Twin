import pandas as pd

def export_results(G):
    rows = []
    for u, v, d in G.edges(data=True):
        rows.append({
            "pipe": f"{u}-{v}",
            "status": d['status'],
            "failure_probability": d.get('failure_prob', 0)
        })

    df = pd.DataFrame(rows)
    df.to_csv("simulation_results.csv", index=False)
    return df