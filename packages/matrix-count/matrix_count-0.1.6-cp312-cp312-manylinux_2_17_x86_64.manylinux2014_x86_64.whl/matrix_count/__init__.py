"""
Copyright (c) 2025 Max Jerdee. All rights reserved.

matrix-count: Counting and sampling non-negative integer matrices given margin sums.
"""

from __future__ import annotations

# first party imports
from matrix_count._util import (
    erdos_gallai_check,
    log_binom,
    log_factorial,
    log_factorial2,
    log_sum_exp,
)
from matrix_count.count import count_log_symmetric_matrices
from matrix_count.estimate import estimate_log_symmetric_matrices
from matrix_count.sample import sample_symmetric_matrix

from ._version import version as __version__

__all__ = [
    "__version__",
    "log_binom",
    "log_factorial",
    "log_factorial2",
    "log_sum_exp",
    "erdos_gallai_check",
    "count_log_symmetric_matrices",
    "estimate_log_symmetric_matrices",
    "sample_symmetric_matrix",
]
