# Example of how samples can be combined to compute averages of functions of symmetric matrices with given margins.
# In this case the average product of two off-diagonal entries is computed.

from __future__ import annotations

import numpy as np

import matrix_count

samples = []
entropies = []
log_correlators = []

correlator_sum = 0
total_prop = 0
num_samples = 10000

for _t in range(num_samples):
    sample, entropy = matrix_count.sample_symmetric_matrix([20, 11, 3])
    samples.append(sample)
    entropies.append(entropy)
    log_correlators.append(np.log(sample[0, 1] * sample[1, 2]))

entropies = np.array(entropies)
log_correlators = np.array(log_correlators)

# Expectations can be calculated as E[f(A)] = 1/(\sum_{A_i} 1/Q(A_i))\sum_{A_i} f(A_i)/Q(A_i)
# where Q(A_i) = exp(-entropy(A_i))
log_correlator = matrix_count.log_sum_exp(log_correlators + entropies) - matrix_count.log_sum_exp(entropies)
log_correlator_squared = matrix_count.log_sum_exp(2 * log_correlators + entropies) - matrix_count.log_sum_exp(
    entropies
)
log_correlator_std = 0.5 * (
    np.log(np.exp(0) - np.exp(2 * log_correlator - log_correlator_squared))
    + log_correlator_squared
)

log_correlator_err_est = np.exp(
    log_correlator_std - 0.5 * np.log(len(entropies)) - log_correlator
)

print(
    f"Range of correlator: {np.exp(log_correlator)} +/- {np.exp(log_correlator)*log_correlator_err_est}"
)
