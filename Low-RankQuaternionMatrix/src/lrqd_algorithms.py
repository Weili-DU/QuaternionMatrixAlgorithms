import numpy as np

from src.quaternion_ops import (
    as_quaternion_matrix,
    fro_norm,
    fro_norm_sq,
    project_observed,
    quat_conj_transpose,
    quat_matmul,
)


def _check_inputs(d: np.ndarray, mask: np.ndarray, rank: int, alpha: float, eps: float, max_iter: int) -> None:
    d = as_quaternion_matrix(d)
    if mask.shape != d.shape[:2]:
        raise ValueError("Mask shape must match data matrix first two dimensions.")
    if not np.issubdtype(mask.dtype, np.bool_):
        raise ValueError("Mask must be boolean.")
    if rank <= 0 or rank >= min(d.shape[0], d.shape[1]):
        raise ValueError("Rank must satisfy 0 < rank < min(m, n).")
    if alpha <= 0 or eps <= 0 or max_iter <= 0:
        raise ValueError("alpha, eps and max_iter must be positive.")


def _init_variables(d: np.ndarray, mask: np.ndarray, rank: int, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    m, n, _ = d.shape
    rng = np.random.default_rng(seed)
    a = np.zeros((m, n, 4), dtype=np.float64)
    a[mask] = d[mask]
    missing = ~mask
    a[missing, 1:] = rng.random((int(np.sum(missing)), 3))
    h = rng.standard_normal((m, rank, 4)) * 0.05
    w = rng.standard_normal((rank, n, 4)) * 0.05
    return a, h, w


def _objective(a: np.ndarray, h: np.ndarray, w: np.ndarray) -> float:
    r = quat_matmul(h, w) - a
    return 0.5 * fro_norm_sq(r)


def run_algorithm1(
    d: np.ndarray,
    mask: np.ndarray,
    rank: int,
    alpha: float,
    eps: float,
    max_iter: int,
    seed: int = 0,
) -> dict:
    _check_inputs(d, mask, rank, alpha, eps, max_iter)
    a, h, w = _init_variables(d, mask, rank, seed)
    history = []
    for k in range(max_iter):
        a_prev, h_prev, w_prev = a.copy(), h.copy(), w.copy()
        r_hw_a = quat_matmul(h, w) - a
        h = h - alpha * quat_matmul(r_hw_a, quat_conj_transpose(w))
        r_hnew_w_a = quat_matmul(h, w) - a
        w = w - alpha * quat_matmul(quat_conj_transpose(h), r_hnew_w_a)
        r_hnew_wnew_a = quat_matmul(h, w) - a
        a_new = a - alpha * (a - quat_matmul(h, w))
        a_new = project_observed(a_new, d, mask)
        a = a_new
        delta = np.sqrt(
            fro_norm_sq(a - a_prev) + fro_norm_sq(h - h_prev) + fro_norm_sq(w - w_prev)
        )
        obj = _objective(a, h, w)
        history.append({"iter": k + 1, "obj": obj, "delta": float(delta)})
        if delta < eps:
            break
    return {"A": a, "H": h, "W": w, "history": history}


def run_algorithm2(
    d: np.ndarray,
    mask: np.ndarray,
    rank: int,
    alpha: float,
    eps: float,
    max_iter: int,
    seed: int = 0,
) -> dict:
    _check_inputs(d, mask, rank, alpha, eps, max_iter)
    a, h, w = _init_variables(d, mask, rank, seed)
    history = []
    for k in range(max_iter):
        a_prev, h_prev, w_prev = a.copy(), h.copy(), w.copy()
        r_hw_a = quat_matmul(h, w) - a
        h = h - alpha * quat_matmul(r_hw_a, quat_conj_transpose(w))
        r_hnew_w_a = quat_matmul(h, w) - a
        w = w - alpha * quat_matmul(quat_conj_transpose(h), r_hnew_w_a)
        a_new = quat_matmul(h, w)
        a_new = project_observed(a_new, d, mask)
        a = a_new
        delta = np.sqrt(
            fro_norm_sq(a - a_prev) + fro_norm_sq(h - h_prev) + fro_norm_sq(w - w_prev)
        )
        obj = _objective(a, h, w)
        history.append({"iter": k + 1, "obj": obj, "delta": float(delta)})
        if delta < eps:
            break
    return {"A": a, "H": h, "W": w, "history": history}


def extract_rgb(a: np.ndarray) -> np.ndarray:
    a = as_quaternion_matrix(a)
    rgb = np.clip(a[:, :, 1:], 0.0, 1.0)
    return rgb


def degraded_to_rgb(d: np.ndarray) -> np.ndarray:
    d = as_quaternion_matrix(d)
    return np.clip(d[:, :, 1:], 0.0, 1.0)


def convergence_delta(result: dict) -> float:
    h = result["history"]
    if not h:
        return float("inf")
    return float(h[-1]["delta"])


def iteration_count(result: dict) -> int:
    return len(result["history"])


def objective_value(result: dict) -> float:
    h = result["history"]
    if not h:
        return float("inf")
    return float(h[-1]["obj"])

