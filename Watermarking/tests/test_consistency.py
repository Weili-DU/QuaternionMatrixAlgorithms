from __future__ import annotations

import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.io_utils import generate_demo_host, generate_demo_watermark
from src.metrics import compute_nc
from src.watermarking import embed_watermark, extract_watermark


class TestEmbedExtractConsistency(unittest.TestCase):
    def test_no_attack_consistency(self) -> None:
        np.random.seed(7)
        host = generate_demo_host(size=256)
        watermark = generate_demo_watermark(size=64)
        watermarked, key, _ = embed_watermark(host, watermark, rho=0.3, arnold_iters=3)
        extracted = extract_watermark(watermarked, key)
        nc = compute_nc(np.mean(watermark, axis=2), np.mean(extracted, axis=2))
        self.assertGreater(nc, 0.8)


if __name__ == "__main__":
    unittest.main()
