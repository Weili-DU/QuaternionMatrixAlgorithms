from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class Quaternion:
    w: float
    x: float
    y: float
    z: float

    @staticmethod
    def zero() -> "Quaternion":
        return Quaternion(0.0, 0.0, 0.0, 0.0)

    @staticmethod
    def one() -> "Quaternion":
        return Quaternion(1.0, 0.0, 0.0, 0.0)

    def __add__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: "Quaternion | float") -> "Quaternion":
        if isinstance(other, (int, float)):
            return Quaternion(self.w * other, self.x * other, self.y * other, self.z * other)
        w1, x1, y1, z1 = self.w, self.x, self.y, self.z
        w2, x2, y2, z2 = other.w, other.x, other.y, other.z
        return Quaternion(
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        )

    def __rmul__(self, other: float) -> "Quaternion":
        return self * other

    def conj(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def squared_norm(self) -> float:
        return self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z

    def norm(self) -> float:
        return math.sqrt(self.squared_norm())

    def inverse(self) -> "Quaternion":
        n2 = self.squared_norm()
        if n2 == 0.0:
            raise ZeroDivisionError("Quaternion inverse failed because norm is zero.")
        c = self.conj()
        return Quaternion(c.w / n2, c.x / n2, c.y / n2, c.z / n2)

    def is_close(self, other: "Quaternion", tol: float = 1e-10) -> bool:
        return (
            abs(self.w - other.w) <= tol
            and abs(self.x - other.x) <= tol
            and abs(self.y - other.y) <= tol
            and abs(self.z - other.z) <= tol
        )

    def to_array(self) -> np.ndarray:
        return np.array([self.w, self.x, self.y, self.z], dtype=float)


@dataclass(frozen=True)
class DualQuaternion:
    primal: Quaternion
    dual: Quaternion

    @staticmethod
    def zero() -> "DualQuaternion":
        return DualQuaternion(Quaternion.zero(), Quaternion.zero())

    @staticmethod
    def one() -> "DualQuaternion":
        return DualQuaternion(Quaternion.one(), Quaternion.zero())

    def __add__(self, other: "DualQuaternion") -> "DualQuaternion":
        return DualQuaternion(self.primal + other.primal, self.dual + other.dual)

    def __sub__(self, other: "DualQuaternion") -> "DualQuaternion":
        return DualQuaternion(self.primal - other.primal, self.dual - other.dual)

    def __mul__(self, other: "DualQuaternion") -> "DualQuaternion":
        return DualQuaternion(
            self.primal * other.primal,
            self.primal * other.dual + self.dual * other.primal,
        )

    def primal_norm(self) -> float:
        return self.primal.norm()

    def conjugate(self) -> "DualQuaternion":
        return DualQuaternion(self.primal.conj(), self.dual.conj())

    def is_close(self, other: "DualQuaternion", tol: float = 1e-10) -> bool:
        return self.primal.is_close(other.primal, tol=tol) and self.dual.is_close(other.dual, tol=tol)
