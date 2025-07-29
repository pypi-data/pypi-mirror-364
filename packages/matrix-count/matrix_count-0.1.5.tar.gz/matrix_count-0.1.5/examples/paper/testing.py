# Doing some tests

import matrix_count
import numpy as np
import matplotlib.pyplot as plt

# test_margin = [2, 16, 14, 30, 9, 24, 11, 25, 12, 4, 12, 8, 11, 11, 24, 1, 8, 10, 13, 16, 20, 9, 13, 12, 8, 19, 22, 7, 19, 1, 6, 3]

# estimate, err = matrix_count.count_log_symmetric_matrices(test_margin, binary_matrix=True)
# print(estimate, err)

# print(matrix_count.erdos_gallai_check(test_margin))

# print(erdos_gallai_check_parts(test_margin))

test_margin = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 49, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 14, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 15, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 259, 1, 1]

# Take samples
num_samples = 1000
entropies = []
for _ in range(num_samples):
    sample, entropy = matrix_count.sample_symmetric_matrix(test_margin)
    entropies.append(entropy)

# Plot hist
plt.hist(entropies, bins=50)
plt.savefig("testing.png")
print(entropies)
