from __future__ import annotations

import numpy as np

from src.cqmath import CQMatrix


def example61() -> tuple[CQMatrix, CQMatrix]:
    a1 = np.array(
        [
            [1, 2, 4],
            [2, 5, 3],
            [4, -2, 2],
        ],
        dtype=np.float64,
    )
    a2 = np.array(
        [
            [1, 2, -1],
            [-1, 1, -1],
            [1, -1, 3],
        ],
        dtype=np.float64,
    )
    a3 = np.array(
        [
            [1, 2, 1],
            [-2, -2, 1],
            [2, -1, 8],
        ],
        dtype=np.float64,
    )
    a4 = np.array(
        [
            [3, 5, 2],
            [-6, 1, -1],
            [5, 3, -1],
        ],
        dtype=np.float64,
    )
    b1 = np.array([[-2], [8], [2]], dtype=np.float64)
    b2 = np.array([[1], [-2], [-1]], dtype=np.float64)
    b3 = np.array([[1], [1], [1]], dtype=np.float64)
    b4 = np.array([[3], [4], [1]], dtype=np.float64)
    return CQMatrix.from_components(a1, a2, a3, a4), CQMatrix.from_components(b1, b2, b3, b4)


def random_cq_matrix(m: int, n: int, seed: int = 0, dtype: str = "float64") -> CQMatrix:
    if dtype not in {"float32", "float64"}:
        raise ValueError(f"不支持的 dtype: {dtype}")
    dt = np.float32 if dtype == "float32" else np.float64
    rng = np.random.default_rng(seed)
    a1 = rng.random((m, n), dtype=dt)
    a2 = rng.random((m, n), dtype=dt)
    a3 = rng.random((m, n), dtype=dt)
    a4 = rng.random((m, n), dtype=dt)
    return CQMatrix.from_components(a1, a2, a3, a4)


def random_cq_vector(m: int, seed: int = 0, dtype: str = "float64") -> CQMatrix:
    if dtype not in {"float32", "float64"}:
        raise ValueError(f"不支持的 dtype: {dtype}")
    dt = np.float32 if dtype == "float32" else np.float64
    rng = np.random.default_rng(seed)
    b1 = rng.random((m, 1), dtype=dt)
    b2 = rng.random((m, 1), dtype=dt)
    b3 = rng.random((m, 1), dtype=dt)
    b4 = rng.random((m, 1), dtype=dt)
    return CQMatrix.from_components(b1, b2, b3, b4)
