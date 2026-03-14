from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.cqmath import cqls_via_gi, cqls_via_svd, iterative_refine_cqls, penrose_error, pinv_cq, residual_norm, svdcq
from src.example_data import example61, random_cq_matrix, random_cq_vector

OUT_FIG = ROOT / "outputs" / "figures"
OUT_TAB = ROOT / "outputs" / "tables"
OUT_LOG = ROOT / "outputs" / "logs"


def ensure_dirs() -> None:
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    OUT_TAB.mkdir(parents=True, exist_ok=True)
    OUT_LOG.mkdir(parents=True, exist_ok=True)


def run_example61(rcond: float = 1e-12) -> dict:
    a, b = example61()
    svd_pack = svdcq(a)
    x1 = cqls_via_svd(a, b, rcond=rcond)
    x2 = cqls_via_gi(a, b, rcond=rcond)
    a_dag = pinv_cq(a, rcond=rcond)
    p_err = penrose_error(a, a_dag)
    rec_err = (a - (svd_pack["U"] @ svd_pack["Sigma"] @ svd_pack["V"].h())).fro_norm()
    return {
        "example": "6.1",
        "svd_residual": residual_norm(a, x1, b),
        "gi_residual": residual_norm(a, x2, b),
        "x_diff_norm": (x1 - x2).fro_norm(),
        "reconstruction_error": rec_err,
        "penrose_e1": p_err["e1"],
        "penrose_e2": p_err["e2"],
        "penrose_e3": p_err["e3"],
        "penrose_e4": p_err["e4"],
        "paper_trend_match": bool(residual_norm(a, x1, b) < 1e-11 and residual_norm(a, x2, b) < 1e-11),
    }


def run_scan(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for dtype in cfg["dtype_grid"]:
        for init in cfg["init_grid"]:
            for rcond in cfg["rcond_grid"]:
                for tol in cfg["tol_grid"]:
                    for max_iter in cfg["max_iter_grid"]:
                        residuals = []
                        times = []
                        for m in cfg["size_grid"]:
                            n = m
                            seed = int(cfg["base_seed"] + m)
                            a = random_cq_matrix(m, n, seed=seed, dtype=dtype)
                            b = random_cq_vector(m, seed=seed + 17, dtype=dtype)
                            t0 = time.perf_counter()
                            x, iters, res = iterative_refine_cqls(
                                a=a,
                                b=b,
                                rcond=float(rcond),
                                max_iter=int(max_iter),
                                tol=float(tol),
                                init=init,
                                seed=seed + 33,
                            )
                            dt = time.perf_counter() - t0
                            residuals.append(float(residual_norm(a, x, b)))
                            times.append(float(dt))
                        rows.append(
                            {
                                "dtype": dtype,
                                "init": init,
                                "rcond": float(rcond),
                                "tol": float(tol),
                                "max_iter": int(max_iter),
                                "mean_residual": float(np.mean(residuals)),
                                "max_residual": float(np.max(residuals)),
                                "mean_time_sec": float(np.mean(times)),
                                "trend_match": bool(np.max(residuals) < 1e-11),
                            }
                        )
    scan_df = pd.DataFrame(rows).sort_values(["trend_match", "max_residual", "mean_time_sec"], ascending=[False, True, True])

    best = scan_df.iloc[0]
    curve_rows = []
    for m in cfg["size_grid"]:
        seed = int(cfg["base_seed"] + m)
        a = random_cq_matrix(m, m, seed=seed, dtype=best["dtype"])
        b = random_cq_vector(m, seed=seed + 17, dtype=best["dtype"])
        t0 = time.perf_counter()
        x, iters, res = iterative_refine_cqls(
            a=a,
            b=b,
            rcond=float(best["rcond"]),
            max_iter=int(best["max_iter"]),
            tol=float(best["tol"]),
            init=best["init"],
            seed=seed + 33,
        )
        dt = time.perf_counter() - t0
        curve_rows.append({"size": m, "residual": residual_norm(a, x, b), "time_sec": dt, "iters": iters})
    curve_df = pd.DataFrame(curve_rows)
    return scan_df, curve_df


def make_figures(curve_df: pd.DataFrame) -> None:
    plt.figure(figsize=(7, 4))
    plt.semilogy(curve_df["size"], curve_df["residual"], marker="o", label="Reproduced residual")
    plt.axhline(1e-11, color="r", linestyle="--", label="Paper trend threshold 1e-11")
    plt.xlabel("Matrix size m=n")
    plt.ylabel("Residual ||Ax-b||_F")
    plt.title("CQLS residual trend")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_FIG / "residual_trend.png", dpi=180)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(curve_df["size"], curve_df["time_sec"], marker="s")
    plt.xlabel("Matrix size m=n")
    plt.ylabel("Runtime (s)")
    plt.title("Runtime trend")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_FIG / "runtime_trend.png", dpi=180)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=str(ROOT / "configs" / "default_scan.json"))
    args = parser.parse_args()

    ensure_dirs()
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    ex = run_example61(rcond=min(cfg["rcond_grid"]))
    scan_df, curve_df = run_scan(cfg)

    pd.DataFrame([ex]).to_csv(OUT_TAB / "example61_metrics.csv", index=False)
    scan_df.to_csv(OUT_TAB / "parameter_scan.csv", index=False)
    curve_df.to_csv(OUT_TAB / "best_combo_curve.csv", index=False)

    best = scan_df.iloc[0].to_dict()
    compare = pd.DataFrame(
        [
            {
                "metric": "Error trend",
                "paper": "All errors < 1e-11",
                "reproduced": f"max residual={best['max_residual']:.3e}",
                "aligned": bool(best["max_residual"] < 1e-11),
            },
            {
                "metric": "Algorithm consistency",
                "paper": "CQLS Alg1 and Alg2 produce same minimum-norm solution",
                "reproduced": f"x_diff_norm={ex['x_diff_norm']:.3e}",
                "aligned": bool(ex["x_diff_norm"] < 1e-10),
            },
        ]
    )
    compare.to_csv(OUT_TAB / "paper_comparison.csv", index=False)

    make_figures(curve_df)
    with open(OUT_LOG / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump({"example61": ex, "best_config": best}, f, indent=2, ensure_ascii=False)
    print("Reproduction finished. Tables/Figures/Logs are saved under outputs/.")


if __name__ == "__main__":
    main()
