# Examples of typical usage of the matrix_count module

import matrix_count

# Margin of a 8x8 symmetric non-negative integer matrix with even diagonal entries
# margin = [10, 9, 8, 7, 6, 5, 4, 3]
margin = [3, 4, 5, 6, 7, 8, 9, 10]

# Estimate the logarithm of the number of symmetric matrices with given margin sum
# (number of multigraphs with given degree sequence)
estimate = matrix_count.estimate_log_symmetric_matrices(margin, alpha=1)
print("Estimated log count of symmetric matrices:", estimate)

# Count the number of such matrices
count, count_err = matrix_count.count_log_symmetric_matrices(
    margin, alpha=1
)
print("Log count of symmetric matrices:", count, "+/-", count_err)

# Sample from the space of such matrices
num_samples = 3
for _t in range(num_samples):
    sample, entropy = matrix_count.sample_symmetric_matrix(margin)
    print("Sampled matrix:")
    print(sample)
    print("Minus log probability of sampled matrix:", entropy)