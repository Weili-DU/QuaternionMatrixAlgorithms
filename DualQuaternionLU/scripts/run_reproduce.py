from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import (
    banded_structured_matrix,
    random_matrix,
    dq_lu,
    dq_lu_structure_preserving,
    reconstruct_from_lu,
    permuted_original,
    matrix_sub,
    frobenius_norm,
    primal_nonzero_count,
)


def relative_reconstruction_error(a: np.ndarray, p: np.ndarray, l: np.ndarray, u: np.ndarray) -> float:
    pa = permuted_original(a, p)
    lu = reconstruct_from_lu(type("Tmp", (), {"l": l, "u": u})())
    diff = matrix_sub(pa, lu)
    denom = frobenius_norm(pa)
    if denom == 0.0:
        return 0.0
    return frobenius_norm(diff) / denom


def fill_ratio(a: np.ndarray, l: np.ndarray, u: np.ndarray) -> float:
    n = a.shape[0]
    nnz_a = primal_nonzero_count(a)
    nnz_lu = primal_nonzero_count(l) + primal_nonzero_count(u) - n
    if nnz_a == 0:
        return 0.0
    return float(nnz_lu / nnz_a)


def permutation_change_ratio(p: np.ndarray) -> float:
    n = len(p)
    moved = int(np.sum(p != np.arange(n)))
    return moved / n


def run_experiment(config: dict) -> list[dict]:
    rng = np.random.default_rng(config["seed"])
    n_small = config["n_small"]
    n_main = config["n_main"]
    a_small = random_matrix(n_small, rng=rng, scale=0.2, dual_scale=0.05)
    a_struct = banded_structured_matrix(n_main, rng=rng, bandwidth=config["bandwidth"])

    res_std_small = dq_lu(a_small, pivoting=True, pivot_tol=config["pivot_tol"])
    err_std_small = relative_reconstruction_error(a_small, res_std_small.p, res_std_small.l, res_std_small.u)

    res_std = dq_lu(a_struct, pivoting=True, pivot_tol=config["pivot_tol"])
    err_std = relative_reconstruction_error(a_struct, res_std.p, res_std.l, res_std.u)
    fill_std = fill_ratio(permuted_original(a_struct, res_std.p), res_std.l, res_std.u)
    perm_std = permutation_change_ratio(res_std.p)

    res_sp = dq_lu_structure_preserving(
        a_struct,
        diagonal_shift=config["diagonal_shift"],
        pivot_tol=config["pivot_tol"],
    )
    err_sp = relative_reconstruction_error(a_struct, res_sp.p, res_sp.l, res_sp.u)
    fill_sp = fill_ratio(permuted_original(a_struct, res_sp.p), res_sp.l, res_sp.u)
    perm_sp = permutation_change_ratio(res_sp.p)

    return [
        {
            "method": "standard_partial_pivot",
            "matrix_size": n_main,
            "relative_error": err_std,
            "fill_ratio": fill_std,
            "permutation_change_ratio": perm_std,
            "small_scale_error": err_std_small,
        },
        {
            "method": "structure_preserving_no_pivot",
            "matrix_size": n_main,
            "relative_error": err_sp,
            "fill_ratio": fill_sp,
            "permutation_change_ratio": perm_sp,
            "small_scale_error": err_std_small,
        },
    ]


def write_outputs(rows: list[dict]) -> None:
    logs_dir = ROOT / "outputs" / "logs"
    fig_dir = ROOT / "outputs" / "figures"
    tab_dir = ROOT / "outputs" / "tables"
    logs_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    tab_dir.mkdir(parents=True, exist_ok=True)

    csv_path = tab_dir / "comparison_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["method", "matrix_size", "relative_error", "fill_ratio", "permutation_change_ratio", "small_scale_error"],
        )
        writer.writeheader()
        writer.writerows(rows)

    md_path = tab_dir / "comparison_table.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("| method | matrix_size | relative_error | fill_ratio | permutation_change_ratio | small_scale_error |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        for r in rows:
            f.write(
                f"| {r['method']} | {r['matrix_size']} | {r['relative_error']:.4e} | "
                f"{r['fill_ratio']:.4f} | {r['permutation_change_ratio']:.4f} | {r['small_scale_error']:.4e} |\n"
            )

    methods = [r["method"] for r in rows]
    errors = [r["relative_error"] for r in rows]
    perm = [r["permutation_change_ratio"] for r in rows]
    x = np.arange(len(methods))

    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.bar(x - 0.18, errors, width=0.36, label="relative_error")
    ax1.set_yscale("log")
    ax1.set_ylabel("Relative reconstruction error (log)")
    ax1.set_xticks(x, methods, rotation=10)
    ax2 = ax1.twinx()
    ax2.bar(x + 0.18, perm, width=0.36, color="tab:orange", label="permutation_change_ratio")
    ax2.set_ylabel("Permutation change ratio")
    fig.tight_layout()
    fig.savefig(fig_dir / "error_fill_ratio.png", dpi=180)
    plt.close(fig)

    log_path = logs_dir / "run_summary.json"
    with log_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def main() -> None:
    config_path = ROOT / "configs" / "experiment_config.json"
    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    rows = run_experiment(config)
    write_outputs(rows)
    for row in rows:
        print(
            f"{row['method']}: rel_err={row['relative_error']:.4e}, "
            f"fill_ratio={row['fill_ratio']:.4f}, perm_ratio={row['permutation_change_ratio']:.4f}, "
            f"small_scale_error={row['small_scale_error']:.4e}"
        )


if __name__ == "__main__":
    main()
