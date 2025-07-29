from __future__ import annotations

import logging

import numpy as np
from numpy.typing import ArrayLike

from . import _input_output, _util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def alpha_symmetric_2(
    matrix_total: int, n: int, diagonal_sum: int | None = None, alpha: float = 1.0
) -> float:
    """
    Dirichlet-Multinomial parameter alpha for the second order moment matching estimate
    of the number of symmetric matrices with given conditions.

    Parameters
    ----------
    matrix_total : int
        Matrix total (sum of all entries).
    n : int
        Matrix size (n, n).
    diagonal_sum : int or None, optional
        Sum of the diagonal elements of the matrix.
    alpha : float, optional
        Dirichlet-multinomial parameter, defaults to 1.0.

    Returns
    -------
    float
        alpha
    """
    if diagonal_sum is None:
        log_numerator = _util.log_sum_exp(
            [
                np.log(matrix_total),
                np.log(matrix_total + n * (matrix_total - 1) - 2)
                + np.log(n + 1)
                + np.log(alpha),
            ]
        )  # Overflow prevention

        log_denominator = _util.log_sum_exp(
            [
                np.log(2 * (matrix_total - 1)),
                np.log(n) + np.log((n + 1) * alpha + matrix_total - 2),
            ]
        )  # Overflow prevention

        return float(np.exp(log_numerator - log_denominator))
    # Fixed diagonal sum
    with np.errstate(divide="ignore"):  # Ignore divide by zero warning
        log_numerator = np.real(
            _util.log_sum_exp(
                [
                    np.log(-1 + 0j)
                    + np.log(-1 + n)
                    + 2 * np.log(diagonal_sum)
                    + np.log(2 + (-1 + n) * n * alpha),
                    np.log(-1 + 0j)
                    + np.log(2)
                    + np.log(-1 + n)
                    + np.log(n)
                    + np.log(diagonal_sum)
                    + np.log(alpha)
                    + np.log(2 + (-1 + n) * n * alpha),
                    np.log(n - 1)
                    + 2 * np.log(matrix_total)
                    + np.log(1 + n * alpha)
                    + np.log(2 + (-1 + n) * n * alpha),
                    np.log(-1 + 0j)
                    + np.log(-2 + n)
                    + np.log(matrix_total - diagonal_sum)
                    + np.log(1 + n * alpha)
                    + np.log(matrix_total - diagonal_sum + (-1 + n) * n * alpha),
                ]
            )
        )
        log_denominator = np.real(
            np.log(n)
            + _util.log_sum_exp(
                [
                    np.log(-1 + n)
                    + 2 * np.log(diagonal_sum)
                    + np.log(2 + (-1 + n) * n * alpha),
                    np.log(2)
                    + np.log(-1 + n)
                    + np.log(n)
                    + np.log(diagonal_sum)
                    + np.log(alpha)
                    + np.log(2 + (-1 + n) * n * alpha),
                    np.log(-1 + 0j)
                    + np.log(-1 + n)
                    + np.log(matrix_total)
                    + np.log(1 + n * alpha)
                    + np.log(2 + (-1 + n) * n * alpha),
                    np.log(-2 + n)
                    + np.log(matrix_total - diagonal_sum)
                    + np.log(1 + n * alpha)
                    + np.log(matrix_total - diagonal_sum + (-1 + n) * n * alpha),
                ]
            )
        )
        return float(np.exp(log_numerator - log_denominator))


def alpha_symmetric_3(
    matrix_total: int, n: int, diagonal_sum: int | None = None, alpha: float = 1.0
) -> tuple[float, float]:
    """
    Dirichlet-Multinomial parameters alpha_plus and alpha_minus for the third order moment matching estimate
    of the number of symmetric matrices with given conditions.

    Parameters
    ----------
    matrix_total : int
        Matrix total (sum of all entries).
    n : int
        Matrix size (n, n).
    diagonal_sum : int or None, optional
        Sum of the diagonal elements of the matrix.
    alpha : float, optional
        Dirichlet-multinomial parameter, defaults to 1.0.

    Returns
    -------
    tuple of (float, float)
        alpha_plus, alpha_minus
    """
    if diagonal_sum is None:
        log_common_numerator = np.real(
            _util.log_sum_exp(
                [
                    2 * _util.log_c(matrix_total)
                    + _util.log_c(
                        4
                        + n
                        + (1 + n) * (4 + n * (11 + 4 * n)) * alpha
                        + n * (1 + n) ** 3 * (2 + n) * alpha**2
                    ),
                    _util.log_c(1 + n)
                    + _util.log_c(matrix_total)
                    + _util.log_c(
                        -4
                        + alpha
                        * (
                            -12
                            + n
                            * (
                                -17
                                - 11 * n
                                - (1 + n) * (7 + n * (4 + 3 * n)) * alpha
                                + n * (1 + n) ** 3 * alpha**2
                            )
                        )
                    ),
                    _util.log_c(1 + n)
                    + 2 * _util.log_c(alpha)
                    + _util.log_c(
                        8
                        + n
                        * (
                            4
                            + alpha * (2 + n * (7 + 2 * n - (1 + n) * (4 + n) * alpha))
                        )
                    ),
                ]
            )
        )

        log_sqrt_term = np.real(
            0.5
            * (
                _util.log_c(-1 + alpha + n * alpha)
                + _util.log_c(matrix_total - (1 + n) * alpha)
                + _util.log_c(matrix_total + n * (1 + n) * alpha)
                + _util.log_c(
                    -4
                    - 4 * n
                    + 4 * matrix_total
                    + 3 * n * matrix_total
                    + n * (1 + n) * (n * (-1 + matrix_total) + matrix_total) * alpha
                )
                + _util.log_c(
                    4 * (-1 + matrix_total)
                    + n
                    * (
                        -4
                        + 5 * matrix_total
                        + (1 + n)
                        * (-5 + 4 * matrix_total + n * (-4 + 5 * matrix_total))
                        * alpha
                        + n
                        * (1 + n) ** 2
                        * (-2 + n * (-1 + matrix_total) + matrix_total)
                        * alpha**2
                    )
                )
            )
        )

        log_denominator = np.real(
            _util.log_sum_exp(
                [
                    _util.log_c(8 * (1 + n) ** 2),
                    _util.log_c(-2)
                    + _util.log_c(1 + n)
                    + _util.log_c(8 + 5 * n)
                    + _util.log_c(matrix_total),
                    _util.log_c(2 * (4 + n * (5 + 2 * n)))
                    + 2 * _util.log_c(matrix_total),
                    _util.log_c(n * (1 + n) * alpha)
                    + _util.log_c(
                        2 * n * (1 + 2 * n)
                        - 3 * n * (3 + n) * matrix_total
                        + (4 + n * (3 + n)) * matrix_total**2
                        - 2 * (1 + matrix_total)
                    ),
                    2 * _util.log_c(n * (1 + n) * alpha)
                    + _util.log_c(-3 + n * (-5 + matrix_total) + 5 * matrix_total),
                    _util.log_c(2)
                    + 3 * (_util.log_c(n) + _util.log_c(1 + n) + _util.log_c(alpha)),
                ]
            )
        )

        alpha_plus = np.real(
            np.exp(
                _util.log_sum_exp([log_common_numerator, log_sqrt_term])
                - log_denominator
            )
        )
        alpha_minus = np.real(
            np.exp(
                _util.log_sum_exp(
                    [log_common_numerator, np.log(-1 + 0j) + log_sqrt_term]
                )
                - log_denominator
            )
        )

        return alpha_plus, alpha_minus
    # Fixed diagonal sum
    raise NotImplementedError


def alpha_symmetric_binary(matrix_total: int, n: int) -> float:
    """
    Dirichlet-Multinomial parameter alpha for the second order moment matching estimate
    of the number of binary symmetric matrices. Note that this will typically be negative, and not a valid Dirichlet-Multinomial parameter.

    Parameters
    ----------
    matrix_total : int
        Matrix total (sum of all entries).
    n : int
        Matrix size (n, n).

    Returns
    -------
    float
        alpha
    """
    alpha_epsilon = 1e-10  # To avoid division by zero
    return (-matrix_total * n + n - 1) / (matrix_total + n - 1 + alpha_epsilon)


def estimate_log_symmetric_matrices(
    row_sums: list[int] | ArrayLike,
    *,
    diagonal_sum: int | None = None,
    index_partition: list[int] | None = None,
    block_sums: ArrayLike | None = None,
    alpha: float = 1.0,
    force_second_order: bool = False,
    binary_matrix: bool = False,
    binary_multinomial_estimate: bool = False,
    verbose: bool = False,
) -> float:
    """
    Dirichlet-multinomial moment-matching estimate of the logarithm
    of the number of symmetric non-negative matrices with given row sums.

    Parameters
    ----------
    row_sums : ArrayLike
        Row sums of the matrix. Length n array-like of non-negative integers.
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
    force_second_order : bool, optional
        Whether to force the use of the second order estimate. Defaults to False.
    binary_matrix : bool, optional
        Whether the matrix is binary (0 or 1) instead of non-negative integer valued. Defaults to False.
    binary_multinomial_estimate : bool, optional
        Whether to use the Multinomial estimate for binary matrices instead of the pseudo Dirichlet-Multinomial estimate. Defaults to False.
    verbose : bool, optional
        Whether to print details of calculation. Defaults to False.

    Returns
    -------
    float
        The logarithm of the estimate of the number of symmetric matrices with given row sums and conditions.
    """
    # Check input validity
    _input_output.log_symmetric_matrices_check_arguments(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        alpha=alpha,
        force_second_order=force_second_order,
        verbose=verbose,
    )

    # Remove empty margins
    row_sums, diagonal_sum, index_partition, block_sums = _input_output.simplify_input(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        verbose=verbose,
    )

    # Check for hardcoded cases
    hardcoded_result = _input_output.log_symmetric_matrices_hardcoded(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        alpha=alpha,
        verbose=verbose,
    )

    if hardcoded_result is not None:
        return hardcoded_result

    matrix_total: int = np.sum(row_sums)
    n = len(row_sums)

    if not binary_matrix:  # Symmetric, non-negative matrices
        if (
            diagonal_sum is None
        ):  # Symmetric, non-negative matrices, no diagonal constraint
            if (
                force_second_order
            ):  # Only case where we might force use of the second order estimate
                alpha_dm = alpha_symmetric_2(
                    matrix_total, n, diagonal_sum=diagonal_sum, alpha=alpha
                )
                result = _util.log_binom(
                    matrix_total / 2 + alpha * n * (n + 1) / 2 - 1,
                    alpha * n * (n + 1) / 2 - 1,
                )
                log_p = -_util.log_binom(
                    matrix_total + n * alpha_dm - 1, n * alpha_dm - 1
                )
                for k in row_sums:
                    log_p += _util.log_binom(k + alpha_dm - 1, alpha_dm - 1)
                result += log_p
                return result
            alpha_plus, alpha_minus = alpha_symmetric_3(
                matrix_total, n, diagonal_sum=diagonal_sum, alpha=alpha
            )
            log_1 = _util.log_binom(
                matrix_total / 2 + alpha * n * (n + 1) / 2 - 1,
                alpha * n * (n + 1) / 2 - 1,
            )
            log_1 += -_util.log_binom(
                matrix_total + n * alpha_plus - 1, n * alpha_plus - 1
            )
            for k in row_sums:
                log_1 += _util.log_binom(k + alpha_plus - 1, alpha_plus - 1)
            log_2 = _util.log_binom(
                matrix_total / 2 + alpha * n * (n + 1) / 2 - 1,
                alpha * n * (n + 1) / 2 - 1,
            )
            log_2 += -_util.log_binom(
                matrix_total + n * alpha_minus - 1, n * alpha_minus - 1
            )
            for k in row_sums:
                log_2 += _util.log_binom(k + alpha_minus - 1, alpha_minus - 1)
            return _util.log_sum_exp([log_1, log_2]) - float(np.log(2))
        # Symmetric, non-negative matrices, diagonal constraint
        alpha_dm = alpha_symmetric_2(
            matrix_total, n, diagonal_sum=diagonal_sum, alpha=alpha
        )
        result = _util.log_binom(diagonal_sum / 2 + alpha * n - 1, alpha * n - 1)
        result += _util.log_binom(
            (matrix_total - diagonal_sum) / 2 + alpha * n * (n - 1) / 2 - 1,
            alpha * n * (n - 1) / 2 - 1,
        )
        result += -_util.log_binom(matrix_total + n * alpha_dm - 1, n * alpha_dm - 1)
        for k in row_sums:
            result += _util.log_binom(k + alpha_dm - 1, alpha_dm - 1)
        return result
    # Symmetric, binary matrices
    if binary_multinomial_estimate:  # Use the multinomial estimate for binary matrices (advantage of never being too far off)
        result = float(
            _util.log_binom(n * (n - 1) / 2, matrix_total / 2)
            - matrix_total * np.log(n)
            + _util.log_factorial(matrix_total)
        )
        for k in row_sums:
            result -= _util.log_factorial(k)
        # Dirichlet-multinomial weight (note that this is a trivial calculation for binary matrices)
        result += matrix_total / 2 * np.log(alpha)
        return result
    alpha_dm = alpha_symmetric_binary(matrix_total, n)
    result = _util.log_binom(n * (n - 1) / 2, matrix_total / 2)
    log_p = -_util.log_binom(matrix_total + n * alpha_dm - 1, n * alpha_dm - 1)
    for k in row_sums:
        log_p += _util.log_binom(k + alpha_dm - 1, alpha_dm - 1)
    result += log_p
    # Dirichlet-multinomial weight (note that this is a trivial calculation for binary matrices)
    result += matrix_total / 2 * np.log(alpha)
    return result
