from __future__ import annotations

from numpy.typing import ArrayLike

def sample_symmetric_matrix_core(
    row_sums: ArrayLike,
    diagonal_sum: int | None = None,
    alpha: float = 1.0,
    seed: int | None = None,
) -> tuple[ArrayLike, float]: ...
