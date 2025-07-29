from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

from . import _input_output
from .sample_binary_core import sample_symmetric_binary_matrix_core
from .sample_core import sample_symmetric_matrix_core


def sample_symmetric_matrix(
    row_sums: ArrayLike,
    *,
    binary_matrix: bool = False,
    diagonal_sum: int | None = None,
    index_partition: list[int] | None = None,
    block_sums: ArrayLike | None = None,
    alpha: float = 1.0,
    verbose: bool = False,
    seed: int | None = None,
) -> tuple[ArrayLike, float]:
    """
    Sample a symmetric matrix with given row sums and diagonal sum.

    Parameters
    ----------
    row_sums : ArrayLike
        List of row sums.
    binary_matrix : bool, optional
        Whether the matrix is binary (0 or 1) instead of non-negative integer valued, defaults to False.
    diagonal_sum : int, optional
        Sum of the diagonal elements of the matrix.
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
    verbose : bool, optional
        Whether to print verbose output, defaults to False.
    seed : int, optional
        Seed for the random number generator, defaults to None.

    Returns
    -------
    tuple of (ArrayLike, float)
        A symmetric matrix with given row sums and diagonal sum, and the log probability of the matrix.
    """

    # Check input validity
    _input_output.log_symmetric_matrices_check_arguments(
        row_sums,
        binary_matrix=binary_matrix,
        diagonal_sum=diagonal_sum,
        index_partition=index_partition,
        block_sums=block_sums,
        alpha=alpha,
        verbose=verbose,
    )

    # Notably we do not simplify these cases before passing to the c++ code, since then we would need to undo that simplification when returning samples.

    # TODO: Implement the block_sums constraint and wrap here.

    diagonal_sum = (
        diagonal_sum if diagonal_sum is not None else -1
    )  # -1 means no constraint

    # Seeding the sampler
    seed = int(np.random.default_rng().integers(2**30)) if seed is None else int(seed)

    if binary_matrix:
        return sample_symmetric_binary_matrix_core(row_sums, seed)
    return sample_symmetric_matrix_core(row_sums, diagonal_sum, alpha, seed)
