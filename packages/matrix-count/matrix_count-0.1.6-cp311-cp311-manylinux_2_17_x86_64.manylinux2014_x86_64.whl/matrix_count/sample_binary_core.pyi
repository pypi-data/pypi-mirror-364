from __future__ import annotations

from numpy.typing import ArrayLike

def sample_symmetric_binary_matrix_core(
    row_sums: ArrayLike,
    seed: int | None = None,
) -> tuple[ArrayLike, float]: ...
