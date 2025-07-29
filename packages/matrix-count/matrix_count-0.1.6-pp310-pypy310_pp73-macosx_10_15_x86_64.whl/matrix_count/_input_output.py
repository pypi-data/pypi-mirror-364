# Checking input validity and hard-code checks for the combinatoric problems
from __future__ import annotations

import logging

import numpy as np
from numpy.typing import ArrayLike

from . import _util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_symmetric_matrices_check_arguments(
    row_sums: list[int] | ArrayLike,
    *,
    binary_matrix: bool = False,
    diagonal_sum: int | None = None,
    index_partition: list[int] | None = None,
    block_sums: ArrayLike | None = None,
    alpha: float = 1.0,
    force_second_order: bool = False,
    verbose: bool = False,
) -> None:
    """
    Raises AssertionError for invalid inputs.

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
        A 2D (q, q) symmetric square NumPy array of non-negative integers representing the constrained sum of each block of the matrix.
        A value of None results in no block sum constraint, defaults to None.
    alpha : float, optional
        Dirichlet-multinomial parameter greater than or equal to 0 to weigh the matrices in the sum.
        A value of 1 gives the uniform count of matrices, defaults to 1.
    force_second_order : bool, optional
        Whether to force the use of the second order estimate. Defaults to False.
    verbose : bool, optional
        Whether to print details of calculation. Defaults to False.
    """

    # Checking input validity
    assert isinstance(
        row_sums, (list, np.ndarray)
    ), "row_sums must be a list or np.array"
    assert all(
        isinstance(x, (int, np.int32, np.int64)) for x in row_sums
    ), "All elements in row_sums must be non-negative integers"
    assert all(
        x >= 0 for x in row_sums
    ), "All elements in row_sums must be non-negative integers"
    assert isinstance(binary_matrix, bool), "binary_matrix must be a boolean"
    if binary_matrix:
        n = len(row_sums)  # Matrix size
        assert all(
            k < n for k in row_sums
        ), "All elements in row_sums must be less than the matrix size."

    if diagonal_sum is not None:
        assert isinstance(diagonal_sum, int), "diagonal_sum must be an integer"
        assert diagonal_sum >= 0, "diagonal_sum must be greater than or equal to 0"

    if index_partition is not None:
        assert isinstance(index_partition, list), "index_partition must be a list"
        assert all(
            isinstance(x, int) for x in index_partition
        ), "block_indices must be a list of integers greater than or equal to 1"
        assert all(
            x >= 1 for x in index_partition
        ), "block_indices must be a list of integers greater than or equal to 1"

        # Number of blocks
        q: int = np.max(index_partition)
        if block_sums is not None:
            assert isinstance(
                block_sums, np.ndarray
            ), "block_sums must be a NumPy array"
            assert block_sums.ndim == 2, "block_sums must be a 2D array"
            assert (
                block_sums.shape[0] == block_sums.shape[1]
            ), "block_sums must be a square array"
            assert block_sums.shape == (q, q), "block_sums must have shape (q, q)"
            assert block_sums.dtype == int, "block_sums must be of dtype int"
            assert np.all(
                block_sums >= 0
            ), "All elements in block_sums must be non-negative integers"
    else:
        assert (
            block_sums is None
        ), "index_partition must be provided to impose a constraint with block_sums"

    assert isinstance(alpha, (int, float)), "alpha must be a float"
    assert alpha >= 0, "alpha must be greater than or equal to 0"

    assert isinstance(force_second_order, bool), "force_second_order must be a boolean"

    assert isinstance(verbose, bool), "verbose must be a boolean"


def simplify_input(
    row_sums: list[int] | ArrayLike,
    *,
    binary_matrix: bool = False,
    diagonal_sum: int | None = None,
    index_partition: list[int] | None = None,
    block_sums: ArrayLike | None = None,
    verbose: bool = False,
) -> tuple[
    ArrayLike,
    int | None,
    list[int] | None,
    ArrayLike | None,
]:
    """
    Simplify the input by removing instances where a row sum is 0.

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
        A 2D (q, q) symmetric square NumPy array of non-negative integers representing the constrained sum of each block of the matrix.
        A value of None results in no block sum constraint, defaults to None.
    verbose : bool, optional
        Whether to print details of calculation. Defaults to False.

    Returns
    -------
    tuple of (ArrayLike, int or None, list of int or None, ArrayLike or None)
        Simplified row_sums, diagonal_sum, index_partition, and block_sums.
    """
    # Flipping 0 <-> 1 for binary matrices if most entries are 1
    if binary_matrix:
        n = len(row_sums)
        if np.sum(row_sums) > n * (n - 1) / 2:  # If most entries are 1
            if verbose:
                logger.info("Flipped row sums to binary complement problem.")
            row_sums = np.array(
                [n - 1 - x for x in row_sums]
            )  # Flip all margins to the complement (n-1 possible nonzero entries in each row)
            # Possibly need to simplify again to remove zeros
            return simplify_input(
                row_sums,
                binary_matrix=True,
                diagonal_sum=diagonal_sum,
                index_partition=index_partition,
                block_sums=block_sums,
                verbose=verbose,
            )
    # Remove instances where a row sum is 0
    row_sums = np.array(row_sums)
    removed_indices = np.where(row_sums == 0)[0]
    if len(removed_indices) > 0:
        if verbose:
            logger.info("Removed rows with zero sum.")
        if index_partition is not None:
            index_partition = index_partition[row_sums != 0]
        # TODO: Remove the block_sums cases
        row_sums = row_sums[row_sums != 0]

    return row_sums, diagonal_sum, index_partition, block_sums


def log_symmetric_matrices_hardcoded(
    row_sums: list[int] | ArrayLike,
    *,
    binary_matrix: bool = False,
    diagonal_sum: int | None = None,
    index_partition: list[int] | None = None,
    block_sums: ArrayLike | None = None,
    alpha: float = 1.0,
    verbose: bool = False,
) -> float | None:
    """
    Raises AssertionError for invalid inputs.

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
        A 2D (q, q) symmetric square NumPy array of non-negative integers representing the constrained sum of each block of the matrix.
        A value of None results in no block sum constraint, defaults to None.
    alpha : float, optional
        Dirichlet-multinomial parameter greater than or equal to 0 to weigh the matrices in the sum.
        A value of 1 gives the uniform count of matrices, defaults to 1.
    verbose : bool, optional
        Whether to print details of calculation. Defaults to False.

    Returns
    -------
    float or None
        Logarithm of the number of symmetric matrices satisfying the constraints if hardcoded,
        None if no hardcoding is possible.
    """
    # Checking whether such a matrix is possible
    row_sums = np.array(row_sums)

    matrix_total: int = np.sum(row_sums)

    if matrix_total % 2 == 1:
        if verbose:
            logger.info("No matrices satisfy, margin total is odd")
        return float("-inf")

    n = len(row_sums)  # Matrix size
    if binary_matrix:
        # Check if the provided margin satisfies the Erdos-Gallai condition
        if not _util.erdos_gallai_check(row_sums):
            if verbose:
                logger.info("No matrices satisfy the Erdos-Gallai condition")
            return float("-inf")
    else:
        if diagonal_sum is not None:
            # If the diagonal sum is constrained to be even, the provided diagonal sum must be even
            if diagonal_sum % 2 == 1:
                if verbose:
                    logger.info(
                        "No matrices satisfy the even diagonal condition, given diagonal sum is odd"
                    )
                return float("-inf")

            # Compute the minimum possible diagonal entry that can be achieved (given the given number of off-diagonal edges)
            m_in_min: int = 0
            m_out = np.sum(row_sums) / 2 - diagonal_sum / 2
            for k in row_sums:
                m_in_min += max(0, np.ceil((k - m_out) / 2))

            m_in_max: int = np.sum(np.floor(row_sums / 2))

            if diagonal_sum < 2 * m_in_min or diagonal_sum > 2 * m_in_max:
                if verbose:
                    logger.info("No matrices satisfy the diagonal sum condition.")
                return float("-inf")

        if diagonal_sum == np.sum(row_sums):
            if verbose:
                logger.info("Hardcoded case: all off-diagonal entries are 0")
            return 0.0  # log(1)

        # TODO: Add explicit treatment of alpha = 0
        assert alpha > 0, "alpha must be greater than 0, alpha = 0 is not yet supported"

        # TODO: Add the block sums case
        assert index_partition is None, "block sum constraints are not yet supported"
        assert block_sums is None, "block sum constraints are not yet supported"

    # Explicit case where each margin is 1 (0 entries have been removed), applies whether binary_matrix is True or False
    if matrix_total == n:
        if verbose:
            logger.info("Hardcoded case: each margin is 1")
        # Recursively can compute that there are n!/n!! possible matrices
        return _util.log_factorial(n) - _util.log_factorial2(n)

    return None
