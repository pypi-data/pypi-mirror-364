import matrix_count
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Distribute with a power law
test_margin = []
for i in range(100):
    test_margin.append(int(30*((i+40)/50)**-2))

# test_margin = [3, 3, 2, 2, 2, 2]

if sum(test_margin) % 2 == 1:
    test_margin[-1] += 1

entropies = []
log_path_lengths = []

avg_path_lengths = []
avg_path_lengths_err = []

for _ in range(1000):
    # Generate the configuration model graph
    sample, entropy = matrix_count.sample_symmetric_matrix(test_margin, binary_matrix=True)
    print(entropy)

    # Create a NetworkX graph from the sample
    G = nx.Graph()
    for i in range(len(sample)):
        for j in range(i):
            if sample[i][j] == 1:
                G.add_edge(i, j)

    # Compute the shortest path length between two specific nodes
    start_node = 10
    end_node = 20

    try:
        path_length = nx.shortest_path_length(G, source=start_node, target=end_node)
        print(f"Shortest path length between node {start_node} and node {end_node} is {path_length}")
    except nx.NetworkXNoPath:
        path_length = -1
        print(f"No path found between node {start_node} and node {end_node}")
    
    entropies.append(entropy)
    log_path_lengths.append(np.log(path_length))

    entropies_np = np.array(entropies)
    log_path_lengths_np = np.array(log_path_lengths)

    # Expectations can be calculated as E[f(A)] = 1/(\sum_{A_i} 1/Q(A_i))\sum_{A_i} f(A_i)/Q(A_i)
    # where Q(A_i) = exp(-entropy(A_i))
    log_path_length = matrix_count.log_sum_exp(log_path_lengths_np + entropies_np) - matrix_count.log_sum_exp(entropies_np)
    log_path_length_squared = matrix_count.log_sum_exp(2 * log_path_lengths_np + entropies_np) - matrix_count.log_sum_exp(
        entropies_np
    )
    log_path_length_std = 0.5 * (
        np.log(np.exp(0) - np.exp(2 * log_path_length - log_path_length_squared))
        + log_path_length_squared
    )

    log_path_length_err_est = np.exp(
        log_path_length_std - 0.5 * np.log(len(entropies)) - log_path_length
    )

    print(
        f"Range of path_length: {np.exp(log_path_length)} +/- {np.exp(log_path_length)*log_path_length_err_est}"
    )
    
    avg_path_lengths.append(np.exp(log_path_length))
    avg_path_lengths_err.append(np.exp(log_path_length) * log_path_length_err_est)

# Plot the average path length over time
plt.plot(avg_path_lengths)
plt.errorbar(range(len(avg_path_lengths)), avg_path_lengths, yerr=avg_path_lengths_err)
plt.xlabel("Number of samples")
plt.ylabel("Average path length")
plt.savefig("path_length.png")

print(log_path_lengths)
print(entropies)
