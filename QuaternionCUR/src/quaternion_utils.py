import numpy as np


def validate_quaternion_matrix(a: np.ndarray, name: str = "A") -> None:
    if not isinstance(a, np.ndarray):
        raise TypeError(f"{name} must be a numpy.ndarray")
    if a.ndim != 3 or a.shape[2] != 4:
        raise ValueError(f"{name} must have shape (m, n, 4)")
    if a.shape[0] == 0 or a.shape[1] == 0:
        raise ValueError(f"{name} must be non-empty")
    if not np.isfinite(a).all():
        raise ValueError(f"{name} contains non-finite values")


def quaternion_entry_abs(a: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(a * a, axis=2))


def q_to_complex_block(a: np.ndarray) -> np.ndarray:
    validate_quaternion_matrix(a, "A")
    m, n, _ = a.shape
    z1 = a[:, :, 0] + 1j * a[:, :, 1]
    z2 = a[:, :, 2] + 1j * a[:, :, 3]
    top = np.hstack([z1, z2])
    bottom = np.hstack([-np.conjugate(z2), np.conjugate(z1)])
    out = np.vstack([top, bottom])
    if out.shape != (2 * m, 2 * n):
        raise RuntimeError("Internal error: invalid complex block shape")
    return out


def complex_block_to_q(x: np.ndarray, m: int, n: int) -> np.ndarray:
    if x.ndim != 2:
        raise ValueError("x must be 2D")
    if x.shape != (2 * m, 2 * n):
        raise ValueError("x shape must be (2m, 2n)")
    z11 = x[:m, :n]
    z12 = x[:m, n:]
    z21 = x[m:, :n]
    z22 = x[m:, n:]
    a = 0.5 * (z11 + np.conjugate(z22))
    b = 0.5 * (z12 - np.conjugate(z21))
    out = np.empty((m, n, 4), dtype=float)
    out[:, :, 0] = np.real(a)
    out[:, :, 1] = np.imag(a)
    out[:, :, 2] = np.real(b)
    out[:, :, 3] = np.imag(b)
    validate_quaternion_matrix(out, "Q")
    return out


def q_matmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    validate_quaternion_matrix(a, "A")
    validate_quaternion_matrix(b, "B")
    if a.shape[1] != b.shape[0]:
        raise ValueError("Shape mismatch for quaternion matrix multiplication")
    m, _, _ = a.shape
    _, n, _ = b.shape
    cblk = q_to_complex_block(a) @ q_to_complex_block(b)
    return complex_block_to_q(cblk, m, n)


def q_pinv(a: np.ndarray, rcond: float = 1e-12) -> np.ndarray:
    validate_quaternion_matrix(a, "A")
    m, n, _ = a.shape
    cblk = q_to_complex_block(a)
    cblk_pinv = np.linalg.pinv(cblk, rcond=rcond)
    return complex_block_to_q(cblk_pinv, n, m)


def q_fro_norm(a: np.ndarray) -> float:
    validate_quaternion_matrix(a, "A")
    return float(np.linalg.norm(a.reshape(-1), ord=2))


def relative_error(a: np.ndarray, b: np.ndarray) -> float:
    validate_quaternion_matrix(a, "A")
    validate_quaternion_matrix(b, "B")
    if a.shape != b.shape:
        raise ValueError("A and B must have the same shape")
    denom = q_fro_norm(a)
    if denom <= 0:
        raise ValueError("Norm of A is zero")
    return q_fro_norm(a - b) / denom


def quaternion_rgb_psnr(original: np.ndarray, reconstructed: np.ndarray, data_range: float = 1.0) -> float:
    validate_quaternion_matrix(original, "original")
    validate_quaternion_matrix(reconstructed, "reconstructed")
    if original.shape != reconstructed.shape:
        raise ValueError("original and reconstructed must have same shape")
    rgb_original = original[:, :, 1:4]
    rgb_reconstructed = reconstructed[:, :, 1:4]
    mse = float(np.mean((rgb_original - rgb_reconstructed) ** 2))
    if mse <= 1e-16:
        return 120.0
    return float(10.0 * np.log10((data_range**2) / mse))


def make_quaternion_from_rgb(rgb: np.ndarray) -> np.ndarray:
    if not isinstance(rgb, np.ndarray):
        raise TypeError("rgb must be a numpy.ndarray")
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("rgb must have shape (m, n, 3)")
    if not np.isfinite(rgb).all():
        raise ValueError("rgb contains non-finite values")
    m, n, _ = rgb.shape
    out = np.zeros((m, n, 4), dtype=float)
    out[:, :, 1:] = rgb
    validate_quaternion_matrix(out, "Q")
    return out


def to_image_rgb(a: np.ndarray) -> np.ndarray:
    validate_quaternion_matrix(a, "A")
    rgb = np.clip(a[:, :, 1:4], 0.0, 1.0)
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise RuntimeError("Internal error: invalid RGB shape")
    return rgb
