from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from .split_quaternion import SplitQuaternionMatrix, from_components, from_sigma, to_sigma
from .svdsq import SVDSQConfig, relative_error, solve_min_norm_ls, svdsq


@dataclass
class ScanConfig:
    random_seed: int
    rcond: float
    rank_tol: float
    epsilon_clip: float
    max_iter: int
    refinement_tol: float
    normal_eq_ridge: float


def _ensure_dirs(root: Path) -> None:
    for rel in [
        "paper",
        "src",
        "scripts",
        "configs",
        "tests",
        "outputs/figures",
        "outputs/tables",
        "outputs/logs",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)


def example61_matrices() -> Dict[str, SplitQuaternionMatrix]:
    A = from_components(
        [[3, 4, -8], [-2, 1, 9], [1, 3, -1]],
        [[10, 3, -7], [6, 2, 3], [2, -3, 5]],
        [[2, 7, 2], [-4, 1, 7], [2, 1, 8]],
        [[7, 1, -1], [1, 3, 2], [2, 1, 7]],
    )
    B = from_components(
        [[2, 1], [4, 0], [5, 3]],
        [[3, 6], [0, 3], [2, 0]],
        [[1, 3], [4, 0], [0, 1]],
        [[2, 4], [0, 2], [4, 0]],
    )
    return {"A": A, "B": B}


def _random_sq(m: int, n: int, rng: np.random.Generator) -> SplitQuaternionMatrix:
    return from_components(
        rng.random((m, n)),
        rng.random((m, n)),
        rng.random((m, n)),
        rng.random((m, n)),
    )


def _normal_equation_solver(
    A: SplitQuaternionMatrix,
    B: SplitQuaternionMatrix,
    ridge: float,
    max_iter: int,
    tol: float,
) -> SplitQuaternionMatrix:
    As = to_sigma(A).astype(np.float32)
    Bs = to_sigma(B).astype(np.float32)
    n = As.shape[1]
    gram = As.T @ As + np.float32(ridge) * np.eye(n, dtype=np.float32)
    rhs = As.T @ Bs
    gram_inv = np.linalg.inv(gram)
    Xs = gram_inv @ rhs
    for _ in range(max_iter):
        residual = Bs - As @ Xs
        delta = gram_inv @ (As.T @ residual)
        Xs_next = Xs + delta
        denom = np.linalg.norm(Xs_next, ord="fro")
        ratio = np.linalg.norm(delta, ord="fro") / (denom + 1e-15)
        Xs = Xs_next
        if ratio < tol:
            break
    return from_sigma(Xs.astype(np.float64))


def _write_table_markdown(path: Path, header: List[str], rows: List[List[str]]) -> None:
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_reproduction(root: Path, config: Dict) -> Dict:
    _ensure_dirs(root)
    matrices = example61_matrices()
    A, B = matrices["A"], matrices["B"]

    svd_cfg = SVDSQConfig(
        rcond=config["scan_grid"][0]["rcond"],
        rank_tol=config["scan_grid"][0]["rank_tol"],
        epsilon_clip=config["scan_grid"][0]["epsilon_clip"],
    )
    example61_result = svdsq(A, config=svd_cfg)
    xls = solve_min_norm_ls(A, B, config=svd_cfg)

    paper_sigma_a = np.array([16.9333, 11.9819, 8.1115], dtype=np.float64)
    paper_sigma_c = np.array([10.0567, 9.1327, 7.8331], dtype=np.float64)
    ours_sigma_a = example61_result.sigma_a[:3]
    ours_sigma_c = example61_result.sigma_c[:3]
    sigma_rel_gap = float(
        np.linalg.norm(np.concatenate([ours_sigma_a - paper_sigma_a, ours_sigma_c - paper_sigma_c]), ord=2)
        / np.linalg.norm(np.concatenate([paper_sigma_a, paper_sigma_c]), ord=2)
    )

    comp_rows = []
    for i in range(3):
        comp_rows.append(
            [
                f"σ{i+1}",
                f"{paper_sigma_a[i]:.4f}+{paper_sigma_c[i]:.4f}j",
                f"{ours_sigma_a[i]:.4f}+{ours_sigma_c[i]:.4f}j",
                f"{abs(ours_sigma_a[i]-paper_sigma_a[i]):.3e}",
                f"{abs(ours_sigma_c[i]-paper_sigma_c[i]):.3e}",
            ]
        )
    _write_table_markdown(
        root / "outputs/tables/example61_sigma_compare.md",
        ["指标", "论文", "复现", "a误差", "j系数误差"],
        comp_rows,
    )

    grid: List[ScanConfig] = [ScanConfig(**item) for item in config["scan_grid"]]
    scales = config["scales"]
    best_row = None
    scan_rows_csv = ["seed,rcond,rank_tol,epsilon_clip,max_iter,refine_tol,ridge,mean_err_svd,mean_err_ne,mean_time_svd,mean_time_ne,score"]
    fig_x, fig_y_svd, fig_y_ne = [], [], []

    for cfg in grid:
        rng = np.random.default_rng(cfg.random_seed)
        err_svd_all, err_ne_all = [], []
        time_svd_all, time_ne_all = [], []
        for h in scales:
            m = n = 10 * h
            p = 5 * h
            X_true = _random_sq(n, p, rng)
            A_rand = _random_sq(m, n, rng)
            B_rand = from_sigma(to_sigma(A_rand) @ to_sigma(X_true))

            t0 = time.perf_counter()
            X_svd = solve_min_norm_ls(
                A_rand,
                B_rand,
                config=SVDSQConfig(rcond=cfg.rcond, rank_tol=cfg.rank_tol, epsilon_clip=cfg.epsilon_clip),
            )
            t1 = time.perf_counter()

            t2 = time.perf_counter()
            X_ne = _normal_equation_solver(
                A_rand,
                B_rand,
                ridge=cfg.normal_eq_ridge,
                max_iter=cfg.max_iter,
                tol=cfg.refinement_tol,
            )
            t3 = time.perf_counter()

            err_svd_all.append(relative_error(X_true, X_svd))
            err_ne_all.append(relative_error(X_true, X_ne))
            time_svd_all.append(t1 - t0)
            time_ne_all.append(t3 - t2)

        mean_err_svd = float(np.mean(err_svd_all))
        mean_err_ne = float(np.mean(err_ne_all))
        mean_time_svd = float(np.mean(time_svd_all))
        mean_time_ne = float(np.mean(time_ne_all))
        score = mean_err_svd + 0.1 * mean_time_svd

        row = {
            "seed": cfg.random_seed,
            "rcond": cfg.rcond,
            "rank_tol": cfg.rank_tol,
            "epsilon_clip": cfg.epsilon_clip,
            "max_iter": cfg.max_iter,
            "refine_tol": cfg.refinement_tol,
            "ridge": cfg.normal_eq_ridge,
            "mean_err_svd": mean_err_svd,
            "mean_err_ne": mean_err_ne,
            "mean_time_svd": mean_time_svd,
            "mean_time_ne": mean_time_ne,
            "score": score,
        }
        if best_row is None or row["score"] < best_row["score"]:
            best_row = row
        scan_rows_csv.append(
            ",".join(
                [
                    str(row["seed"]),
                    f"{row['rcond']:.1e}",
                    f"{row['rank_tol']:.1e}",
                    f"{row['epsilon_clip']:.1e}",
                    str(row["max_iter"]),
                    f"{row['refine_tol']:.1e}",
                    f"{row['ridge']:.1e}",
                    f"{row['mean_err_svd']:.6e}",
                    f"{row['mean_err_ne']:.6e}",
                    f"{row['mean_time_svd']:.6e}",
                    f"{row['mean_time_ne']:.6e}",
                    f"{row['score']:.6e}",
                ]
            )
        )

        if cfg == grid[0]:
            fig_x = scales
            fig_y_svd = err_svd_all
            fig_y_ne = err_ne_all

    (root / "outputs/tables/parameter_scan.csv").write_text("\n".join(scan_rows_csv), encoding="utf-8")

    plt.figure(figsize=(7.2, 4.5))
    plt.plot(fig_x, fig_y_svd, marker="o", label="SVDLS (paper method)")
    plt.plot(fig_x, fig_y_ne, marker="s", label="Normal-equation baseline")
    plt.xlabel("Scale h (m=n=10h, p=5h)")
    plt.ylabel("Relative error")
    plt.yscale("log")
    plt.title("Error trend: SVDLS vs baseline")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(root / "outputs/figures/error_trend.png", dpi=150)
    plt.close()

    trend_rows = []
    for idx, h in enumerate(fig_x):
        trend_rows.append([str(h), f"{fig_y_svd[idx]:.3e}", f"{fig_y_ne[idx]:.3e}"])
    _write_table_markdown(
        root / "outputs/tables/trend_table.md",
        ["h", "SVDLS相对误差", "基线相对误差"],
        trend_rows,
    )

    summary = {
        "example61_sigma_rel_gap": sigma_rel_gap,
        "best_scan": best_row,
        "example61_ours_sigma": [
            [float(ours_sigma_a[0]), float(ours_sigma_c[0])],
            [float(ours_sigma_a[1]), float(ours_sigma_c[1])],
            [float(ours_sigma_a[2]), float(ours_sigma_c[2])],
        ],
        "xls_fro_norm": float(np.linalg.norm(to_sigma(xls), ord="fro")),
    }
    (root / "outputs/logs/reproduce_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary
