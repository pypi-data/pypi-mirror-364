from __future__ import annotations

import numpy as np
import pytest

from matrix_count._util import (
    erdos_gallai_check,
    log_binom,
    log_factorial,
    log_factorial2,
    log_sum_exp,
    log_weight,
)


def test_log_factorial():
    n = 5
    result = 1
    for i in range(1, n + 1, 1):
        result *= i
    assert log_factorial(n) == pytest.approx(np.log(result))


def test_log_factorial2():
    n = 5
    result = 1
    for i in range(1, n + 1, 2):
        result *= i
    assert log_factorial2(n) == pytest.approx(np.log(result))

    n = 6
    result = 1
    for i in range(2, n + 1, 2):
        result *= i
    assert log_factorial2(n) == pytest.approx(np.log(result))


def test_log_binom():
    n = 5
    m = 2
    assert log_binom(n, m) == pytest.approx(np.log(10))


def test_log_sum_exp():
    test_array = [0.0, 1.0, 2.0]
    result = 0
    for a in test_array:
        result += np.exp(a)
    result = np.log(result)
    assert log_sum_exp(test_array) == pytest.approx(result)


def test_log_weight():
    A = np.array([[2, 2, 3], [2, 3, 4], [3, 4, 4]])
    alpha = 5
    result = 17.0292069
    assert log_weight(A, alpha) == pytest.approx(result)


def test_erdos_gallai_check():
    ks = np.array([4, 2, 2, 1, 1])
    assert erdos_gallai_check(ks)

    ks = np.array([4, 3, 1, 1, 1])
    assert not erdos_gallai_check(ks)

    ks = np.array([13, 5, 14, 5, 5, 15, 9, 3, 1, 6, 2, 7, 2, 6, 6, 1])
    assert not erdos_gallai_check(ks)
