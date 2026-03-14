from __future__ import annotations

import numpy as np

from src.split_quaternion import from_components, from_sigma, to_sigma
from src.svdsq import SVDSQConfig, solve_min_norm_ls, svdsq


def test_sigma_roundtrip():
    rng = np.random.default_rng(7)
    A = from_components(
        rng.standard_normal((3, 2)),
        rng.standard_normal((3, 2)),
        rng.standard_normal((3, 2)),
        rng.standard_normal((3, 2)),
    )
    B = from_sigma(to_sigma(A))
    assert np.allclose(A.a, B.a)
    assert np.allclose(A.b, B.b)
    assert np.allclose(A.c, B.c)
    assert np.allclose(A.d, B.d)


def test_svdsq_reconstruction_small():
    rng = np.random.default_rng(11)
    A = from_components(
        rng.standard_normal((3, 3)),
        rng.standard_normal((3, 3)),
        rng.standard_normal((3, 3)),
        rng.standard_normal((3, 3)),
    )
    result = svdsq(A, config=SVDSQConfig(rcond=1e-12, rank_tol=1e-12, epsilon_clip=1e-15))
    from src.svdsq import reconstruct

    A_hat = reconstruct(result)
    rel = np.linalg.norm(to_sigma(A) - to_sigma(A_hat), ord="fro") / np.linalg.norm(to_sigma(A), ord="fro")
    assert rel < 1e-10


def test_least_squares_exact_case():
    rng = np.random.default_rng(23)
    A = from_components(
        rng.standard_normal((4, 4)),
        rng.standard_normal((4, 4)),
        rng.standard_normal((4, 4)),
        rng.standard_normal((4, 4)),
    )
    X = from_components(
        rng.standard_normal((4, 2)),
        rng.standard_normal((4, 2)),
        rng.standard_normal((4, 2)),
        rng.standard_normal((4, 2)),
    )
    B = from_sigma(to_sigma(A) @ to_sigma(X))
    X_hat = solve_min_norm_ls(A, B, config=SVDSQConfig(rcond=1e-12, rank_tol=1e-12, epsilon_clip=1e-15))
    rel = np.linalg.norm(to_sigma(X) - to_sigma(X_hat), ord="fro") / np.linalg.norm(to_sigma(X), ord="fro")
    assert rel < 1e-10
