from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from skimage import data
from skimage.transform import resize

from .degradation import apply_missing_pixels, random_sampling_mask
from .lrqr_sr import LRQRSRParams, recover_lrqr_sr
from .utils import psnr_ssim, save_json


def _load_benchmark_images(size: int = 256) -> dict[str, np.ndarray]:
    raw = {
        "astronaut": data.astronaut(),
        "coffee": data.coffee(),
        "cat": data.chelsea(),
        "rocket": data.rocket(),
        "camera_rgb": np.stack([data.camera()] * 3, axis=2),
        "hubble": data.hubble_deep_field()[0:700, 0:700, :],
        "immuno": data.immunohistochemistry(),
        "retina": data.retina(),
    }
    out = {}
    for name, img in raw.items():
        out[name] = resize(img, (size, size, 3), preserve_range=True, anti_aliasing=True).astype(np.float64) / 255.0
    return out


def run_single_recovery(output_dir: Path, sample_rate: float, seed: int, params: LRQRSRParams) -> dict:
    images = _load_benchmark_images()
    image_name = "astronaut"
    gt = images[image_name]
    mask = random_sampling_mask(gt.shape[:2], sample_rate=sample_rate, seed=seed)
    obs = apply_missing_pixels(gt, mask)
    rec, history = recover_lrqr_sr(obs, mask, params)

    metrics_obs = psnr_ssim(gt, obs)
    metrics_rec = psnr_ssim(gt, rec)
    payload = {
        "image_name": image_name,
        "sample_rate": sample_rate,
        "seed": seed,
        "params": asdict(params),
        "observed_metrics": metrics_obs,
        "recovered_metrics": metrics_rec,
        "improvement_psnr": metrics_rec["psnr"] - metrics_obs["psnr"],
        "improvement_ssim": metrics_rec["ssim"] - metrics_obs["ssim"],
    }
    save_json(output_dir / "logs" / "single_run_metrics.json", payload)

    fig = plt.figure(figsize=(12, 4))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)
    ax1.imshow(gt)
    ax1.set_title("Original")
    ax2.imshow(obs)
    ax2.set_title(f"Observed SR={sample_rate}")
    ax3.imshow(rec)
    ax3.set_title(f"Recovered PSNR={metrics_rec['psnr']:.2f}")
    for ax in (ax1, ax2, ax3):
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_dir / "figures" / "recovery_triplet.png", dpi=150)
    plt.close(fig)

    fig2 = plt.figure(figsize=(6, 4))
    plt.plot(history["residual"])
    plt.yscale("log")
    plt.xlabel("Iteration")
    plt.ylabel("Relative residual")
    plt.title("ADMM residual curve")
    plt.tight_layout()
    fig2.savefig(output_dir / "figures" / "residual_curve.png", dpi=150)
    plt.close(fig2)
    return payload


def run_parameter_scan(
    output_dir: Path,
    seed: int = 2025,
    image_size: int = 96,
    max_iter: int = 25,
    tol: float = 5e-4,
) -> pd.DataFrame:
    image = _load_benchmark_images(size=image_size)["astronaut"]
    sr_list = [0.5, 0.3, 0.1]

    beta_candidates = [1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1, 5e-1]
    lambda_candidates = [0.01, 0.03, 0.05, 0.07, 0.1, 0.3, 0.5, 0.7, 1.0]
    rank_candidates = [10, 20, 30, 40, 50, 60, 70, 80, 90]

    rows: list[dict] = []
    for sr in sr_list:
        mask = random_sampling_mask(image.shape[:2], sample_rate=sr, seed=seed)
        obs = apply_missing_pixels(image, mask)

        for beta1 in beta_candidates:
            p = LRQRSRParams(lam=0.1, rank=30, beta1=beta1, rho=1.01, beta_max=1.0, tol=tol, max_iter=max_iter)
            rec, _ = recover_lrqr_sr(obs, mask, p)
            m = psnr_ssim(image, rec)
            rows.append({"sweep": "beta1", "sr": sr, "beta1": beta1, "lambda": 0.1, "rank": 30, **m})

        for lam in lambda_candidates:
            p = LRQRSRParams(lam=lam, rank=30, beta1=1e-4, rho=1.01, beta_max=1.0, tol=tol, max_iter=max_iter)
            rec, _ = recover_lrqr_sr(obs, mask, p)
            m = psnr_ssim(image, rec)
            rows.append({"sweep": "lambda", "sr": sr, "beta1": 1e-4, "lambda": lam, "rank": 30, **m})

        target_rank = 40 if sr == 0.5 else 30
        for rank in rank_candidates:
            p = LRQRSRParams(lam=0.07, rank=rank, beta1=1e-4, rho=1.01, beta_max=1.0, tol=tol, max_iter=max_iter)
            rec, _ = recover_lrqr_sr(obs, mask, p)
            m = psnr_ssim(image, rec)
            rows.append({"sweep": "rank", "sr": sr, "beta1": 1e-4, "lambda": 0.07, "rank": rank, "paper_target_rank": target_rank, **m})

    df = pd.DataFrame(rows)
    df.to_csv(output_dir / "tables" / "parameter_scan.csv", index=False)

    summary = []
    for (sweep, sr), part in df.groupby(["sweep", "sr"], sort=True):
        best = part.sort_values("psnr", ascending=False).iloc[0]
        summary.append(
            {
                "sweep": sweep,
                "sr": sr,
                "best_psnr": best["psnr"],
                "best_ssim": best["ssim"],
                "best_beta1": best["beta1"],
                "best_lambda": best["lambda"],
                "best_rank": best["rank"],
            }
        )
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(output_dir / "tables" / "best_params_by_sweep.csv", index=False)

    fig = plt.figure(figsize=(12, 9))
    for idx, (sweep, x_col) in enumerate([("beta1", "beta1"), ("lambda", "lambda"), ("rank", "rank")], start=1):
        ax = fig.add_subplot(3, 1, idx)
        part = df[df["sweep"] == sweep]
        for sr in sr_list:
            sub = part[part["sr"] == sr].sort_values(x_col)
            ax.plot(sub[x_col], sub["psnr"], marker="o", label=f"SR={sr}")
        if sweep == "beta1":
            ax.set_xscale("log")
        ax.set_title(f"PSNR trend over {sweep}")
        ax.set_xlabel(x_col)
        ax.set_ylabel("PSNR")
        ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "figures" / "parameter_trends.png", dpi=150)
    plt.close(fig)
    return df

