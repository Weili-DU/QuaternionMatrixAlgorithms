from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import random_matrix, dq_lu, reconstruct_from_lu, permuted_original, matrix_sub, frobenius_norm


class TestDualQuaternionLU(unittest.TestCase):
    def test_reconstruction_error(self) -> None:
        rng = np.random.default_rng(7)
        a = random_matrix(4, rng=rng, scale=0.2, dual_scale=0.03)
        result = dq_lu(a, pivoting=True)
        pa = permuted_original(a, result.p)
        lu = reconstruct_from_lu(result)
        diff = matrix_sub(pa, lu)
        rel_err = frobenius_norm(diff) / frobenius_norm(pa)
        self.assertLess(rel_err, 1e-8)


if __name__ == "__main__":
    unittest.main()
