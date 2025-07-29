from __future__ import annotations

import numpy as np
import pytest

from matrix_count.count import count_log_symmetric_matrices


def test_count_log_symmetric_matrices_no_constraints():
    sigma_error = 5  # Number of standard deviations to check within

    # 20,11,3
    test_margin = [20, 11, 3]
    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(test_margin)
    log_count_true = np.log(34)  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        test_margin, alpha=5
    )
    log_count_true = np.log(693809375)  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    # 3,3,3,3,2,2
    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        [3, 3, 3, 3, 2, 2]
    )
    log_count_true = 7.51098  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        [3, 3, 3, 3, 2, 2], alpha=5
    )
    log_count_true = 19.8828  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails


def test_count_log_symmetric_matrices_diagonal_sum():
    sigma_error = 5  # Number of standard deviations to check within

    # 20,11,3
    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        [20, 11, 3], diagonal_sum=20
    )
    log_count_true = 1.09861  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        [20, 11, 3], diagonal_sum=20, alpha=5
    )
    log_count_true = 18.4677  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    # 3,3,3,3,2,2
    test_margin = [3, 3, 3, 3, 2, 2]
    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        test_margin, diagonal_sum=10
    )
    log_count_true = 2.77259  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        test_margin, alpha=5, diagonal_sum=10
    )
    log_count_true = 15.6481  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails


def test_count_log_symmetric_binary_matrices():
    sigma_error = 5  # Number of standard deviations to check within

    # 6, 4, 3, 3, 2, 2, 1, 1
    test_margin = [6, 4, 3, 3, 2, 2, 1, 1]
    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        test_margin, binary_matrix=True
    )
    log_count_true = np.log(47)  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails

    # 4, 3, 3, 2, 2, 1, 1, 0
    test_margin = [4, 3, 3, 2, 2, 1, 1, 0]
    (log_count_est, log_count_est_err) = count_log_symmetric_matrices(
        test_margin, binary_matrix=True
    )
    log_count_true = np.log(65)  # Found with brute force
    assert log_count_est == pytest.approx(
        log_count_true, abs=sigma_error * log_count_est_err
    )  # Chance that this just randomly fails
