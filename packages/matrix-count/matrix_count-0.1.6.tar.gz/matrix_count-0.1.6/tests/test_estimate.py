from __future__ import annotations

import numpy as np
import pytest

from matrix_count.estimate import (
    alpha_symmetric_2,
    alpha_symmetric_3,
    alpha_symmetric_binary,
    estimate_log_symmetric_matrices,
)


def test_estimate_log_symmetric_matrices_invalid_arguments():
    # :param row_sums: Row sums of the matrix. Length n array-like of non-negative integers.
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices([-1, 2, 3])

    # :param diagonal_sum: What the sum of the diagonal elements should be constrained to.
    #     Either an integer greater than or equal to 0 or None, resulting in no constraint on the diagonal elements, defaults to None.
    # :type diagonal_sum: int | None, optional
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices([1, 2, 3], diagonal_sum=-1)

    # :param index_partition: A list of length n of integers ranging from 1 to q.
    #     index_partition[i] indicates the block which index i belongs to for the purposes of a block sum constraint.
    #     A value of None results in no block sum constraint, defaults to None.
    # :type index_partition: list of int | None, optional
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices([1, 2, 3], index_partition=[1, 2, -1])

    # :param block_sums: A 2D (q, q) symmetric square NumPy array of integers representing the constrained sum of each block of the matrix.
    #     A value of None results in no block sum constraint, defaults to None.
    # :type block_sums: np.ndarray, shape (q, q), dtype int
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices(
            [1, 2, 3], index_partition=[1, 2, 1], block_sums=np.array([[1, 2], [2, -1]])
        )
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices(
            [1, 2, 3],
            index_partition=[1, 2, 1],
            block_sums=np.array([[1, 2, 3], [2, 1, 3]]),
        )

    # :param alpha: Dirichlet-multinomial parameter greater than or equal to 0 to weigh the matrices in the sum.
    #     A value of 1 gives the uniform count of matrices, defaults to 1
    # :type alpha: float, optional
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices([1, 2, 3], alpha=-0.5)

    # Case: binary_matrix margin is too large
    with pytest.raises(AssertionError):
        estimate_log_symmetric_matrices([1, 2, 3], binary_matrix=True)


def test_estimate_log_symmetric_matrices_no_matrices():
    # Case: diagonal_sum is odd
    assert estimate_log_symmetric_matrices([2, 2, 2], diagonal_sum=3) == -np.inf

    # Case: diagonal_sum is greater than the sum of row_sums
    assert estimate_log_symmetric_matrices([1, 2, 3], diagonal_sum=10) == -np.inf

    # Case: diagonal_sums with no matrices
    assert estimate_log_symmetric_matrices([10, 1, 1], diagonal_sum=2) == -np.inf
    assert estimate_log_symmetric_matrices([2, 2, 2, 2], diagonal_sum=6) == -np.inf

    # Case: block_sums is not None (not yet supported) TODO: check that this is an impossible case
    # assert estimate_log_symmetric_matrices([1, 2, 3], index_partition=[1, 2, 1], block_sums=np.array([[1, 2], [2, 1]])) == -np.inf

    # Case: total of row_sums is odd
    assert estimate_log_symmetric_matrices([1, 2, 2]) == -np.inf

    # Case: total of off-diagonal is odd
    assert estimate_log_symmetric_matrices([1, 2, 3], diagonal_sum=3) == -np.inf


def test_estimate_log_symmetric_matrices_hardcoded():
    # Case: each margin is 1
    assert estimate_log_symmetric_matrices([0, 1, 1, 1, 1]) == pytest.approx(np.log(3))

    # Case: all off-diagonal are 0
    assert estimate_log_symmetric_matrices(
        [2, 2, 2, 2], diagonal_sum=8
    ) == pytest.approx(np.log(1))

    # Case: binary_matrix margins are all n - 1
    assert estimate_log_symmetric_matrices(
        [2, 2, 2], binary_matrix=True
    ) == pytest.approx(np.log(1))

    # Check binary_matrix cases that violate the Erdos-Gallai conditions
    assert (
        estimate_log_symmetric_matrices([4, 3, 1, 1, 1], binary_matrix=True) == -np.inf
    )


def test_alpha_2():
    # Test the second order moment matching estimates (comparing to Mathematica examples)
    assert alpha_symmetric_2(200, 10, diagonal_sum=None, alpha=1.0) == pytest.approx(
        9.75402, 0.001
    )

    assert alpha_symmetric_2(200, 10, diagonal_sum=None, alpha=5.0) == pytest.approx(
        41.168, 0.001
    )

    assert alpha_symmetric_2(200, 10, diagonal_sum=100, alpha=1.0) == pytest.approx(
        3.6041, 0.001
    )

    assert alpha_symmetric_2(200, 10, diagonal_sum=100, alpha=5.0) == pytest.approx(
        13.1526, 0.001
    )

    # Check that the overflow does not get messed up
    # assert alpha_symmetric_2(200,10,diagonal_sum=200, alpha=1.0) == pytest.approx(1.81507, 0.001)


def test_alpha_3():
    # Test the second order moment matching estimates (comparing to Mathematica examples)
    alpha_pm = alpha_symmetric_3(200, 10, diagonal_sum=None, alpha=1.0)
    alpha_pm_true = 13.7998, 7.53246
    assert alpha_pm[0] == pytest.approx(alpha_pm_true[0], 0.001)
    assert alpha_pm[1] == pytest.approx(alpha_pm_true[1], 0.001)

    alpha_pm = alpha_symmetric_3(200, 10, diagonal_sum=None, alpha=5.0)
    alpha_pm_true = 63.6326, 30.4128
    assert alpha_pm[0] == pytest.approx(alpha_pm_true[0], 0.001)
    assert alpha_pm[1] == pytest.approx(alpha_pm_true[1], 0.001)


def test_alpha_symmetric_binary():
    assert alpha_symmetric_binary(40, 10) == pytest.approx(-7.97959, 0.001)


def test_estimate_log_symmetric_matrices():
    # Test the estimate_log_symmetric_matrices function
    assert estimate_log_symmetric_matrices(
        [20, 11, 3], alpha=1, force_second_order=True
    ) == pytest.approx(3.65746, 0.001)
    assert estimate_log_symmetric_matrices(
        [20, 11, 3], alpha=5, force_second_order=True
    ) == pytest.approx(20.3397, 0.001)

    assert estimate_log_symmetric_matrices([20, 11, 3], alpha=1) == pytest.approx(
        3.60119, 0.001
    )
    assert estimate_log_symmetric_matrices([20, 11, 3], alpha=5) == pytest.approx(
        20.3536, 0.001
    )

    assert estimate_log_symmetric_matrices(
        [20, 11, 3], diagonal_sum=20, alpha=1
    ) == pytest.approx(1.29499, 0.001)
    assert estimate_log_symmetric_matrices(
        [20, 11, 3], diagonal_sum=20, alpha=5
    ) == pytest.approx(18.5925, 0.001)

    # Binary matrices
    # pseudo Dirichlet-Multinomial
    assert estimate_log_symmetric_matrices(
        [1, 1, 1, 1, 2], binary_matrix=True
    ) == pytest.approx(1.89415, 0.001)

    assert estimate_log_symmetric_matrices(
        [1, 1, 1, 1, 2], alpha=5, binary_matrix=True
    ) == pytest.approx(6.72247, 0.001)

    # This is a case where direct abilication of the Dirichlet-Multinomial distribution with a negative alpha results in a negative count
    assert estimate_log_symmetric_matrices(
        [1, 1, 1, 1, 1, 1, 6], binary_matrix=True
    ) == pytest.approx(-3.01943, 0.001)

    # Multinomial estimate
    assert estimate_log_symmetric_matrices(
        [1, 1, 1, 1, 2], binary_matrix=True, binary_multinomial_estimate=True
    ) == pytest.approx(1.01697, 0.001)

    assert estimate_log_symmetric_matrices(
        [1, 1, 1, 1, 2], alpha=5, binary_matrix=True, binary_multinomial_estimate=True
    ) == pytest.approx(5.84528, 0.001)
