import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.lrqd_algorithms import (
    degraded_to_rgb,
    extract_rgb,
    iteration_count,
    objective_value,
    run_algorithm1,
    run_algorithm2,
)
from src.quaternion_ops import quat_matmul


def _psnr(x: np.ndarray, y: np.ndarray, data_range: float = 1.0) -> float:
    mse = np.mean((x - y) ** 2)
    if mse <= 1e-16:
        return float("inf")
    return float(20.0 * np.log10(data_range) - 10.0 * np.log10(mse))


def _ssim_channel(x: np.ndarray, y: np.ndarray) -> float:
    c1 = 0.01**2
    c2 = 0.03**2
    mux = float(np.mean(x))
    muy = float(np.mean(y))
    vx = float(np.var(x))
    vy = float(np.var(y))
    vxy = float(np.mean((x - mux) * (y - muy)))
    num = (2.0 * mux * muy + c1) * (2.0 * vxy + c2)
    den = (mux * mux + muy * muy + c1) * (vx + vy + c2)
    return float(num / den)


def _mssi(x: np.ndarray, y: np.ndarray) -> float:
    vals = [_ssim_channel(x[:, :, i], y[:, :, i]) for i in range(3)]
    return float(np.mean(vals))


def _make_synthetic_rgb(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    rank_true = 4
    h = rng.standard_normal((size, rank_true, 4)) * 0.2
    w = rng.standard_normal((rank_true, size, 4)) * 0.2
    a = quat_matmul(h, w)
    rgb = a[:, :, 1:]
    rgb = rgb - np.min(rgb)
    rgb = rgb / (np.max(rgb) + 1e-12)
    return np.clip(rgb, 0.0, 1.0)


def _to_quaternion(rgb: np.ndarray) -> np.ndarray:
    m, n, _ = rgb.shape
    q = np.zeros((m, n, 4), dtype=np.float64)
    q[:, :, 1:] = rgb
    return q


def _degrade(d_full: np.ndarray, rho: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    mask = rng.random(d_full.shape[:2]) < rho
    d = np.zeros_like(d_full)
    d[mask] = d_full[mask]
    return d, mask


def _run_once(cfg: dict, seed: int) -> dict:
    rgb_gt = _make_synthetic_rgb(int(cfg["image_size"]), seed)
    d_full = _to_quaternion(rgb_gt)
    d, mask = _degrade(d_full, float(cfg["rho"]), seed + 1000)
    common = {
        "d": d,
        "mask": mask,
        "rank": int(cfg["rank"]),
        "alpha": float(cfg["alpha"]),
        "eps": float(cfg["eps"]),
        "max_iter": int(cfg["max_iter"]),
    }
    r1 = run_algorithm1(**common, seed=seed + 1)
    r2 = run_algorithm2(**common, seed=seed + 1)
    rec1 = extract_rgb(r1["A"])
    rec2 = extract_rgb(r2["A"])
    degraded = degraded_to_rgb(d)
    return {
        "rgb_gt": rgb_gt,
        "degraded": degraded,
        "rec1": rec1,
        "rec2": rec2,
        "psnr_degraded": _psnr(degraded, rgb_gt),
        "psnr_alg1": _psnr(rec1, rgb_gt),
        "psnr_alg2": _psnr(rec2, rgb_gt),
        "mssi_degraded": _mssi(degraded, rgb_gt),
        "mssi_alg1": _mssi(rec1, rgb_gt),
        "mssi_alg2": _mssi(rec2, rgb_gt),
        "iter_alg1": iteration_count(r1),
        "iter_alg2": iteration_count(r2),
        "obj_alg1": objective_value(r1),
        "obj_alg2": objective_value(r2),
    }


def _write_comparison_table(rows: list[dict], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "image_id",
        "psnr_degraded",
        "mssi_degraded",
        "psnr_alg1",
        "mssi_alg1",
        "psnr_alg2",
        "mssi_alg2",
        "iter_alg1",
        "iter_alg2",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i, r in enumerate(rows, start=1):
            w.writerow(
                {
                    "image_id": f"{i:02d}",
                    "psnr_degraded": f"{r['psnr_degraded']:.4f}",
                    "mssi_degraded": f"{r['mssi_degraded']:.4f}",
                    "psnr_alg1": f"{r['psnr_alg1']:.4f}",
                    "mssi_alg1": f"{r['mssi_alg1']:.4f}",
                    "psnr_alg2": f"{r['psnr_alg2']:.4f}",
                    "mssi_alg2": f"{r['mssi_alg2']:.4f}",
                    "iter_alg1": r["iter_alg1"],
                    "iter_alg2": r["iter_alg2"],
                }
            )


def _write_param_scan_table(rows: list[dict], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "alpha",
        "eps",
        "max_iter",
        "rank",
        "seed",
        "psnr_alg1",
        "psnr_alg2",
        "mssi_alg1",
        "mssi_alg2",
        "psnr_gain_alg2_vs_alg1",
        "mssi_gain_alg2_vs_alg1",
    ]
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "alpha": r["alpha"],
                    "eps": r["eps"],
                    "max_iter": r["max_iter"],
                    "rank": r["rank"],
                    "seed": r["seed"],
                    "psnr_alg1": f"{r['psnr_alg1']:.4f}",
                    "psnr_alg2": f"{r['psnr_alg2']:.4f}",
                    "mssi_alg1": f"{r['mssi_alg1']:.4f}",
                    "mssi_alg2": f"{r['mssi_alg2']:.4f}",
                    "psnr_gain_alg2_vs_alg1": f"{r['psnr_gain']:.4f}",
                    "mssi_gain_alg2_vs_alg1": f"{r['mssi_gain']:.4f}",
                }
            )


def _plot_results(best: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].imshow(np.clip(best["degraded"], 0.0, 1.0))
    ax[0].set_title("Degraded")
    ax[0].axis("off")
    ax[1].imshow(np.clip(best["rec2"], 0.0, 1.0))
    ax[1].set_title("Algorithm2")
    ax[1].axis("off")
    fig.tight_layout()
    fig.savefig(out_dir / "reconstruction_example.png", dpi=150)
    plt.close(fig)

    fig2, ax2 = plt.subplots(1, 1, figsize=(7, 4))
    labels = ["Degraded", "Algorithm1", "Algorithm2"]
    psnr = [best["psnr_degraded"], best["psnr_alg1"], best["psnr_alg2"]]
    mssi = [best["mssi_degraded"], best["mssi_alg1"], best["mssi_alg2"]]
    x = np.arange(len(labels))
    ax2.bar(x - 0.15, psnr, 0.3, label="PSNR")
    ax2.bar(x + 0.15, np.array(mssi) * 30.0, 0.3, label="MSSI x30")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_title("Trend Comparison")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(out_dir / "trend_metrics.png", dpi=150)
    plt.close(fig2)


def run_reproduction(cfg: dict, root: Path) -> dict:
    seeds = list(cfg["seeds"])
    baseline_rows = [_run_once(cfg, s) for s in seeds]
    out_tables = root / "outputs" / "tables"
    _write_comparison_table(baseline_rows, out_tables / "paper_trend_comparison.csv")

    scan_rows = []
    for alpha in cfg["scan"]["alpha"]:
        for eps in cfg["scan"]["eps"]:
            for max_iter in cfg["scan"]["max_iter"]:
                for rank in cfg["scan"]["rank"]:
                    for seed in cfg["scan"]["seed_subset"]:
                        cfg_tmp = dict(cfg)
                        cfg_tmp["alpha"] = alpha
                        cfg_tmp["eps"] = eps
                        cfg_tmp["max_iter"] = max_iter
                        cfg_tmp["rank"] = rank
                        r = _run_once(cfg_tmp, seed)
                        scan_rows.append(
                            {
                                "alpha": alpha,
                                "eps": eps,
                                "max_iter": max_iter,
                                "rank": rank,
                                "seed": seed,
                                "psnr_alg1": r["psnr_alg1"],
                                "psnr_alg2": r["psnr_alg2"],
                                "mssi_alg1": r["mssi_alg1"],
                                "mssi_alg2": r["mssi_alg2"],
                                "psnr_gain": r["psnr_alg2"] - r["psnr_alg1"],
                                "mssi_gain": r["mssi_alg2"] - r["mssi_alg1"],
                                "raw": r,
                            }
                        )
    _write_param_scan_table(scan_rows, out_tables / "parameter_scan.csv")
    best = max(scan_rows, key=lambda x: (x["psnr_gain"], x["mssi_gain"]))
    _plot_results(best["raw"], root / "outputs" / "figures")

    summary = {
        "paper_table_average": {
            "psnr_degraded": float(np.mean([x["psnr_degraded"] for x in baseline_rows])),
            "psnr_alg1": float(np.mean([x["psnr_alg1"] for x in baseline_rows])),
            "psnr_alg2": float(np.mean([x["psnr_alg2"] for x in baseline_rows])),
            "mssi_degraded": float(np.mean([x["mssi_degraded"] for x in baseline_rows])),
            "mssi_alg1": float(np.mean([x["mssi_alg1"] for x in baseline_rows])),
            "mssi_alg2": float(np.mean([x["mssi_alg2"] for x in baseline_rows])),
        },
        "best_scan": {
            "alpha": best["alpha"],
            "eps": best["eps"],
            "max_iter": best["max_iter"],
            "rank": best["rank"],
            "seed": best["seed"],
            "psnr_alg1": best["psnr_alg1"],
            "psnr_alg2": best["psnr_alg2"],
            "mssi_alg1": best["mssi_alg1"],
            "mssi_alg2": best["mssi_alg2"],
            "psnr_gain_alg2_vs_alg1": best["psnr_gain"],
            "mssi_gain_alg2_vs_alg1": best["mssi_gain"],
        },
    }
    out_log = root / "outputs" / "logs" / "run_summary.json"
    out_log.parent.mkdir(parents=True, exist_ok=True)
    out_log.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary

