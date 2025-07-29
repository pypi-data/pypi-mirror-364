# Demonstration of how samples are combined to estimate the count 
# of symmetric matrices with given margins.
# Produces a figure showing convergence to the true count. 

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

import matrix_count
from matrix_count import _util

test_margin = [3, 3, 3, 3, 2, 2]
true_count = np.exp(7.51098) # Found with brute force

num_samples = 10000

# Estimate the number of matrices with given margins
estimate_2 = matrix_count.estimate_log_symmetric_matrices(test_margin, force_second_order=True)

estimate_3 = matrix_count.estimate_log_symmetric_matrices(test_margin)

logEs = []
log_count_err_ests = []

entropies = []
for t in range(num_samples):
    if t % 100 == 0:
        pass
    sample, entropy = matrix_count.sample_symmetric_matrix(test_margin)
    entropies.append(entropy)
    # log(Delta log E) = log(Delta E/E) = 1/2log(E2 - E^2) - 1/2 log(n) - log(E)
    logE2 = _util.log_sum_exp(2 * np.array(entropies)) - np.log(len(entropies))
    logE = _util.log_sum_exp(entropies) - np.log(len(entropies))
    log_std = 0.5 * (np.log(np.exp(0) - np.exp(2 * logE - logE2)) + logE2)
    log_count_err_est = np.exp(log_std - 0.5 * np.log(len(entropies)) - logE)
    logEs.append(logE)
    log_count_err_ests.append(log_count_err_est)

entropies = np.array(entropies)

plot_frequency = 100  # Number of samples between which to plot the result

logEs = np.array(logEs)
log_count_err_ests = np.array(log_count_err_ests)
inds = np.arange(len(logEs), step=plot_frequency)
plt.errorbar(inds, logEs[inds], yerr=log_count_err_ests[inds], label="SIS estimate")
plt.plot(inds, estimate_2 * np.ones(len(inds)), label="Analytic estimate (2nd)")
plt.plot(inds, estimate_3 * np.ones(len(inds)), label="Analytic estimate (3rd)")
if true_count is not None:
    plt.plot(inds, np.log(true_count) * np.ones(len(inds)), label="True count")
plt.xlabel("Number of samples")
plt.ylabel("Log count")
plt.legend()
plt.savefig("sample.png")
