# Use the sample.pyi implementation of SIS in order to obtain counts and error estimates.
from __future__ import annotations

import logging
import time

import numpy as np
import tqdm
from numpy.typing import ArrayLike

from matrix_count._input_output import (
    log_symmetric_matrices_check_arguments,
    log_symmetric_matrices_hardcoded,
    simplify_input,
)
from matrix_count._util import log_sum_exp, log_weight
from matrix_count.sample import sample_symmetric_matrix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def count_log_symmetric_matrices(
    row_sums: list[int],
    *,
    binary_matrix: bool = False,
    diagonal_sum: int | None = None,
    index_partition: list[int] | None = None,
    block_sums: ArrayLike | None = None,
    alpha: float = 1.0,
    max_samples: int = 1000,
    error_target: float = 0.001,
    seed: int | None = None,
    timeout: float = 60.0,  # Timeout in seconds
    verbose: bool = False,
) -> tuple[float, float]:
    """
    Dirichlet-multinomial moment-matching estimate of the logarithm
    of the number of symmetric non-negative matrices with given row sums.

    Parameters
    ----------
    row_sums : ArrayLike
        Row sums of the matrix. Length n array-like of non-negative integers.
    binary_matrix : bool, optional
        Whether the matrix is binary (0 or 1) instead of non-negative integer valued. Defaults to False.
    diagonal_sum : int or None, optional
        What the sum of the diagonal elements should be constrained to.
        Either an integer greater than or equal to 0 or None, resulting in no constraint on the diagonal elements, defaults to None.
    index_partition : list of int or None, optional
        A list of length n of integers ranging from 1 to q.
        index_partition[i] indicates the block which index i belongs to for the purposes of a block sum constraint.
        A value of None results in no block sum constraint, defaults to None.
    block_sums : ArrayLike, optional
        A 2D (q, q) symmetric square NumPy array of integers representing the constrained sum of each block of the matrix.
        A value of None results in no block sum constraint, defaults to None.
    alpha : float, optional
        Dirichlet-multinomial parameter greater than or equal to 0 to weigh the matrices in the sum.
        A value of 1 gives the uniform count of matrices, defaults to 1.
    max_samples : int, optional
        Maximum number of samples to take. Defaults to 1000.
    error_target : float, optional
        Target absolute error in the logarithm of the count. Defaults to 0.01.
    seed : int, optional
        Seed for the random number generator. Defaults to None.
    timeout : float, optional
        Timeout in seconds. Defaults to 60.0.
    verbose : bool, optional
        Whether to print details of calculation. Defaults to False.

    Returns
    -------
    tuple of (float, float)
        log_count_est : The logarithm of the number of symmetric matrices under given conditions.
        err : The estimated absolute error in the logarithm of the count.
    """

    # Check input validity
    log_symmetric_matrices_check_arguments(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        alpha=alpha,
        verbose=verbose,
    )

    # Remove empty margins
    row_sums, diagonal_sum, index_partition, block_sums = simplify_input(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        verbose=verbose,
    )

    # Check for hardcoded cases
    hardcoded_result = log_symmetric_matrices_hardcoded(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        alpha=alpha,
        verbose=verbose,
    )
    if hardcoded_result is not None:
        return (hardcoded_result, 0)  # No error in the hardcoded cases

    # Set seed if provided
    rng = np.random.default_rng(seed)

    # Sample the matrices
    min_num_samples = 10  # Minimum number of samples to take
    entropies = []
    log_count_est = 0  # Estimated log count
    log_count_err_est = np.inf  # Estimated error in the log count
    start_time = time.time()  # Start time for timeout

    # Use tqdm progress bar if verbose, otherwise use a simple range
    if verbose:
        progress_bar = tqdm.tqdm(range(max_samples))
        use_progress_bar = True
        progress_iter = progress_bar
    else:
        progress_bar = None
        use_progress_bar = False
        progress_iter = range(max_samples)  # type: ignore[assignment]

    for sample_num in progress_iter:
        # Check for timeout
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            if verbose:
                logger.info("Timeout reached.")
            break

        # Seed to use for this sample
        sample_seed = int(
            rng.integers(0, 2**31 - 1)
        )  # If the integer is too large it screws up the pybind wrapper
        # pylint seems to not see the binding on the following line
        sample, entropy = sample_symmetric_matrix(  # pylint: disable=unpacking-non-sequence
            row_sums,
            binary_matrix=binary_matrix,
            diagonal_sum=diagonal_sum,
            index_partition=index_partition,
            block_sums=block_sums,
            alpha=alpha,
            seed=sample_seed,
            verbose=verbose,
        )

        entropy += log_weight(
            sample, alpha
        )  # Really should be averaging w(A)/Q(A), entropy = -log Q(A)

        entropies.append(entropy)
        log_count_est = log_sum_exp(entropies) - np.log(len(entropies))

        log_E_entropy_2 = log_sum_exp(2 * np.array(entropies)) - np.log(len(entropies))
        log_E_entropy = log_sum_exp(entropies) - np.log(len(entropies))
        if (
            log_E_entropy_2 - 2 * log_E_entropy > 0.0001
        ):  # Estimate the error by the standard deviation of the counts
            log_std = 0.5 * (
                np.log(np.exp(0) - np.exp(2 * log_E_entropy - log_E_entropy_2))
                + log_E_entropy_2
            )
            log_count_err_est = np.exp(
                log_std - 0.5 * np.log(len(entropies)) - log_E_entropy
            )
            if use_progress_bar and progress_bar is not None:
                progress_bar.set_postfix_str(
                    f"Log count: {log_E_entropy:.3f} +/- {log_count_err_est:.3f}"
                )
            if (
                log_count_err_est < error_target and sample_num >= min_num_samples
            ):  # Terminate if the error is below the target and we have taken enough samples
                break

    return (log_count_est, log_count_err_est)
