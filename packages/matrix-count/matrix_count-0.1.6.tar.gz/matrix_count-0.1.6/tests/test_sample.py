from __future__ import annotations

import numpy as np
import pytest

from matrix_count._util import log_sum_exp
from matrix_count.sample import sample_symmetric_matrix

# sample_symmetric_matrix


def test_sample_symmetric_matrix():
    # Note that this is a random test and the results may vary.
    samples = []
    entropies = []
    log_correlators = []

    num_samples = 1000

    for _ in range(num_samples):
        sample, entropy = sample_symmetric_matrix([20, 11, 3])
        samples.append(sample)
        entropies.append(entropy)
        val = sample[0, 1] * sample[1, 2]
        if val == 0:
            log_correlators.append(-np.inf)
        else:
            log_correlators.append(np.log(val))

    entropies = np.array(entropies)
    log_correlators = np.array(log_correlators)

    # Expectations can be calculated as E[f(A)] = 1/(\sum_{A_i} 1/Q(A_i))\sum_{A_i} f(A_i)/Q(A_i)
    # where Q(A_i) = exp(-entropy(A_i))
    log_correlator = log_sum_exp(log_correlators + entropies) - log_sum_exp(entropies)
    log_correlator_squared = log_sum_exp(2 * log_correlators + entropies) - log_sum_exp(
        entropies
    )
    log_correlator_std = 0.5 * (
        np.log(np.exp(0) - np.exp(2 * log_correlator - log_correlator_squared))
        + log_correlator_squared
    )

    log_correlator_err_est = np.exp(
        log_correlator_std - 0.5 * np.log(len(entropies)) - log_correlator
    )

    sigma_error = 4  # Number of standard deviations to check within
    true_value = 5

    assert log_correlator == pytest.approx(
        np.log(true_value), abs=sigma_error * log_correlator_err_est
    )  # Chance that this just randomly fails
