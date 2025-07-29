# Small helper functions
from __future__ import annotations

from math import lgamma

import numpy as np
from numpy.typing import ArrayLike


def log_factorial(n: float) -> float:
    """Logarithm of factorial of n

    :param n: float
    :type n: float
    :return: log(n!)
    :rtype: float
    """
    return lgamma(n + 1)


def log_factorial2(n: float) -> float:
    """Logarithm of double factorial of n, for integer k, (2k)!! = k!2^k, (2k-1)!! = (2 k)!/(2^k k!)

    :param n: float
    :type n: float
    :return: log(n!!)
    :rtype: float
    """
    if n % 2 == 0:
        k = n / 2
        return log_factorial(k) + k * float(np.log(2))
    k = (n + 1) / 2
    return log_factorial(2 * k) - log_factorial(k) - k * float(np.log(2))


def log_binom(n: float, m: float) -> float:
    """Logarithm of binomial coefficient binomial(n,m)

    :param n: float
    :type n: float
    :param m: float
    :type m: float
    :return: log(binomial(n,m))
    :rtype: float
    """
    return log_factorial(n) - log_factorial(m) - log_factorial(n - m)


def log_sum_exp(x: ArrayLike) -> float | np.complex64:
    """Overflow protected log(sum(exp(x))) of an array x.

    :param x: Array to be summed
    :type x: np.ndarray[np.float_, np.dtype[np.float_]]
    :return: log(sum(exp(x)))
    :rtype: float | np.complex64
    """
    x = np.array(x)
    a: np.float64 | np.complex64 = np.max(x)
    return a + np.log(np.sum(np.exp(x - a)))


def log_c(x: float) -> np.complex64:
    """Version of logarithm that complexifies arguments to deal with negative numbers

    :param x: float
    :type x: float
    :return: log(x)
    :rtype: np.complex64
    """
    return np.log(x + 0j)


def log_weight(A: ArrayLike, alpha: float) -> float:
    """Logarithm of the weight of a matrix A under the Dirichlet-multinomial distribution with parameter alpha

    :param A: Matrix
    :type A: ArrayLike
    :param alpha: Dirichlet-multinomial parameter
    :type alpha: float
    :return: log(weight)
    :rtype: float
    """
    result = 0.0
    for i in range(A.shape[0]):
        for j in range(i + 1, A.shape[1]):
            result += log_binom(A[i, j] + alpha - 1, alpha - 1)
        result += log_binom(A[i, i] / 2 + alpha - 1, alpha - 1)

    return result


def erdos_gallai_check(ks: ArrayLike) -> bool:
    """Check if a sequence is graphical using the Erdos-Gallai theorem

    :param ks: Sequence of non-negative integers
    :type ks: ArrayLike
    :return: Whether the sequence is graphical
    :rtype: bool
    """
    ks = np.array(ks)
    if np.sum(ks) % 2 == 1 or np.any(ks < 0) or np.any(ks > len(ks) - 1):
        return False
    ks = -np.sort(-ks)
    for l_val in range(1, len(ks) + 1):
        left: int = np.sum(ks[:l_val])
        right: int = l_val * (l_val - 1)
        for _ in range(l_val, len(ks)):
            right += min(l_val, ks[_])
        if left > right:
            return False
    return True
