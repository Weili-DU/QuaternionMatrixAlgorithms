from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from .qcur import qcur_auto
from .quaternion_utils import make_quaternion_from_rgb, quaternion_rgb_psnr, validate_quaternion_matrix


@dataclass
class ExperimentRow:
    c: float
    estimated_k: int
    rel_error: float
    psnr: float


def make_synthetic_color_image(m: int, n: int, seed: int) -> np.ndarray:
    if m <= 0 or n <= 0:
        raise ValueError("m and n must be positive")
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, m)
    xx, yy = np.meshgrid(x, y)
    r = 0.6 * np.sin(2.5 * np.pi * xx) * np.cos(1.3 * np.pi * yy) + 0.4 * xx
    g = 0.5 * np.cos(1.8 * np.pi * xx + 0.2) * np.sin(2.2 * np.pi * yy) + 0.5 * yy
    b = 0.4 * np.sin(3.2 * np.pi * (xx + yy)) + 0.6 * (1 - xx * yy)
    rgb = np.stack([r, g, b], axis=2)
    rgb = (rgb - rgb.min()) / (rgb.max() - rgb.min() + 1e-12)
    rgb = np.clip(rgb + 0.01 * rng.normal(size=rgb.shape), 0.0, 1.0)
    return rgb


def run_scan(config_path: str | Path) -> pd.DataFrame:
    config_path = Path(config_path)
    with config_path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    m = int(cfg["data"]["m"])
    n = int(cfg["data"]["n"])
    seed = int(cfg["data"]["seed"])
    cs = [float(v) for v in cfg["scan"]["c_values"]]
    max_rank = int(cfg["scan"]["max_rank"])
    rcond = float(cfg["scan"]["rcond"])
    rgb = make_synthetic_color_image(m, n, seed)
    q = make_quaternion_from_rgb(rgb)
    validate_quaternion_matrix(q, "Q")
    rows: list[ExperimentRow] = []
    for c in cs:
        res = qcur_auto(q, c=c, max_rank=max_rank, use_fast_u=False, rcond=rcond)
        psnr = quaternion_rgb_psnr(q, res.reconstruction, data_range=1.0)
        rows.append(ExperimentRow(c=c, estimated_k=res.rank_estimation, rel_error=res.rel_error, psnr=psnr))
    df = pd.DataFrame([asdict(r) for r in rows])
    return df


def save_outputs(df: pd.DataFrame, output_dir: str | Path) -> dict:
    output_dir = Path(output_dir)
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    logs_dir = output_dir / "logs"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    paper_table4 = pd.DataFrame(
        {
            "c": [8e-3, 5e-3, 2e-3, 9e-4, 6e-4, 3e-4],
            "paper_k": [35, 63, 152, 252, 301, 374],
            "paper_psnr": [21.2012, 23.1728, 26.7414, 29.4764, 30.8243, 33.2794],
        }
    )
    merged = paper_table4.merge(df, on="c", how="left")
    merged["k_trend_match"] = merged["estimated_k"].diff().fillna(0) >= 0
    merged["psnr_trend_match"] = merged["psnr"].diff().fillna(0) >= 0
    table_path = tables_dir / "table4_like_comparison.csv"
    merged.to_csv(table_path, index=False, encoding="utf-8-sig")

    fig_path = figures_dir / "trend_k_psnr_vs_c.png"
    x = np.arange(len(merged))
    labels = [f"{v:.1e}" for v in merged["c"].to_numpy()]
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(x, merged["paper_k"], "-o", label="Paper k", color="#1f77b4")
    ax1.plot(x, merged["estimated_k"], "-o", label="Reproduced k", color="#2ca02c")
    ax1.set_ylabel("Rank estimation k")
    ax1.set_xticks(x, labels)
    ax1.set_xlabel("Relative error parameter c")
    ax2 = ax1.twinx()
    ax2.plot(x, merged["paper_psnr"], "--s", label="Paper PSNR", color="#ff7f0e")
    ax2.plot(x, merged["psnr"], "--s", label="Reproduced PSNR", color="#d62728")
    ax2.set_ylabel("PSNR")
    lines, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels1 + labels2, loc="lower right")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)

    log_path = logs_dir / "run_summary.txt"
    trend_ok = bool(merged["k_trend_match"].all() and merged["psnr_trend_match"].all())
    with log_path.open("w", encoding="utf-8") as f:
        f.write("Trend check against paper Table 4-like behavior\n")
        f.write(f"k monotonic nondecreasing: {bool(merged['k_trend_match'].all())}\n")
        f.write(f"PSNR monotonic nondecreasing: {bool(merged['psnr_trend_match'].all())}\n")
        f.write(f"overall_trend_match: {trend_ok}\n")
    return {"table": str(table_path), "figure": str(fig_path), "log": str(log_path), "trend_ok": trend_ok}
