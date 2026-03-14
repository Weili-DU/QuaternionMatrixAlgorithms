from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.experiments import run_parameter_scan, run_single_recovery  # noqa: E402
from src.lrqr_sr import LRQRSRParams  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/default.json")
    args = parser.parse_args()

    repo_root = REPO_ROOT
    config_path = repo_root / args.config
    config = json.loads(config_path.read_text(encoding="utf-8"))

    output_dir = repo_root / "outputs"
    params = LRQRSRParams(
        lam=float(config["single_run"]["lambda"]),
        rank=int(config["single_run"]["rank"]),
        beta1=float(config["single_run"]["beta1"]),
        rho=float(config["single_run"]["rho"]),
        beta_max=float(config["single_run"]["beta_max"]),
        tol=float(config["single_run"]["tol"]),
        max_iter=int(config["single_run"]["max_iter"]),
    )

    run_single_recovery(
        output_dir=output_dir,
        sample_rate=float(config["single_run"]["sample_rate"]),
        seed=int(config["single_run"]["seed"]),
        params=params,
    )
    run_parameter_scan(
        output_dir=output_dir,
        seed=int(config["scan"]["seed"]),
        image_size=int(config["scan"]["image_size"]),
        max_iter=int(config["scan"]["max_iter"]),
        tol=float(config["scan"]["tol"]),
    )
    print("Reproduction run completed.")


if __name__ == "__main__":
    main()

