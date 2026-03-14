import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.deim import mdeim_indices
from src.qcur import qcur_decompose
from src.quaternion_utils import make_quaternion_from_rgb, quaternion_rgb_psnr


def test_mdeim_unique_indices():
    rng = np.random.default_rng(0)
    w = rng.normal(size=(30, 8))
    s = mdeim_indices(w)
    assert s.shape == (8,)
    assert len(np.unique(s)) == 8
    assert np.all((0 <= s) & (s < 30))


def test_qcur_runs_on_small_matrix():
    rng = np.random.default_rng(1)
    rgb = rng.uniform(0.0, 1.0, size=(48, 36, 3))
    q = make_quaternion_from_rgb(rgb)
    out = qcur_decompose(q, k=10, use_fast_u=False, rcond=1e-10)
    assert out.reconstruction.shape == q.shape
    assert np.isfinite(out.rel_error)
    assert out.rel_error < 1.0
    psnr = quaternion_rgb_psnr(q, out.reconstruction)
    assert psnr > 10.0
