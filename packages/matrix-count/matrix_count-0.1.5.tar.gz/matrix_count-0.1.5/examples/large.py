# Examples of matrix_count usage on a large example, 
# progress bar shows current progress and estimated value of the log count.

import matrix_count

# Margin of a large symmetric non-negative integer matrix with even diagonal entries
margin = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5]

# Estimate the logarithm of the number of symmetric matrices with given margin sum
# (number of multigraphs with given degree sequence)
estimate = matrix_count.estimate_log_symmetric_matrices(margin, verbose=True, alpha=1)
print("Estimated log count of symmetric matrices:", estimate)

# Count the number of such matrices
count, count_err = matrix_count.count_log_symmetric_matrices(
    margin, verbose=True, alpha=1, timeout=10
)
print("Log count of symmetric matrices:", count, "+/-", count_err)

# Sample from the space of such matrices
num_samples = 3
for _t in range(num_samples):
    sample, entropy = matrix_count.sample_symmetric_matrix(margin)
    print("Sampled matrix:")
    print(sample)
    print("Minus log probability of sampled matrix:", entropy)
