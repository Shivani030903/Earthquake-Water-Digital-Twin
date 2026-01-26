from models.network_generator import generate_network

nodes, pipes = generate_network(n_nodes=30)

print("Generated nodes:", nodes)
print("Generated pipes:", pipes)
