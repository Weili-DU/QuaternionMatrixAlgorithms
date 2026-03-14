import numpy as np


def as_quaternion_matrix(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 3 or x.shape[2] != 4:
        raise ValueError("Quaternion matrix must have shape (m, n, 4).")
    if not np.isfinite(x).all():
        raise ValueError("Quaternion matrix contains non-finite values.")
    return x


def quat_conj_transpose(a: np.ndarray) -> np.ndarray:
    a = as_quaternion_matrix(a)
    out = np.transpose(a, (1, 0, 2)).copy()
    out[:, :, 1:] *= -1.0
    return out


def quat_matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = as_quaternion_matrix(a)
    b = as_quaternion_matrix(b)
    if a.shape[1] != b.shape[0]:
        raise ValueError("Inner dimensions do not match for quaternion matmul.")
    a0, a1, a2, a3 = a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3]
    b0, b1, b2, b3 = b[:, :, 0], b[:, :, 1], b[:, :, 2], b[:, :, 3]
    c0 = a0 @ b0 - a1 @ b1 - a2 @ b2 - a3 @ b3
    c1 = a0 @ b1 + a1 @ b0 + a2 @ b3 - a3 @ b2
    c2 = a0 @ b2 - a1 @ b3 + a2 @ b0 + a3 @ b1
    c3 = a0 @ b3 + a1 @ b2 - a2 @ b1 + a3 @ b0
    return np.stack([c0, c1, c2, c3], axis=2)


def fro_norm(x: np.ndarray) -> float:
    x = as_quaternion_matrix(x)
    return float(np.sqrt(np.sum(x * x)))


def fro_norm_sq(x: np.ndarray) -> float:
    x = as_quaternion_matrix(x)
    return float(np.sum(x * x))


def project_observed(a: np.ndarray, d: np.ndarray, mask: np.ndarray) -> np.ndarray:
    a = as_quaternion_matrix(a)
    d = as_quaternion_matrix(d)
    if mask.shape != a.shape[:2]:
        raise ValueError("Mask shape must be (m, n).")
    out = a.copy()
    out[mask] = d[mask]
    return out

