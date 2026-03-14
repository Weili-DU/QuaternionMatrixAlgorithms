from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.append(str(ROOT))

from src.attacks import build_attacks
from src.io_utils import generate_demo_host, generate_demo_watermark, read_image, save_image, save_triplet_panel
from src.metrics import compute_nc, compute_psnr, compute_ssim
from src.watermarking import embed_watermark, extract_watermark


def ensure_data(host_path: Path, watermark_path: Path) -> None:
    if not host_path.exists():
        save_image(host_path, generate_demo_host(size=512))
    if not watermark_path.exists():
        save_image(watermark_path, generate_demo_watermark(size=64))


def to_gray(img: np.ndarray) -> np.ndarray:
    return np.mean(img.astype(np.float64), axis=2)


def evaluate_one(host: np.ndarray, watermark: np.ndarray, rho: float, arnold_iters: int, arnold_params: tuple[int, int, int, int]):
    watermarked, key, _ = embed_watermark(
        host_rgb=host,
        watermark_rgb=watermark,
        rho=rho,
        arnold_iters=arnold_iters,
        arnold_params=arnold_params,
    )
    extracted = extract_watermark(watermarked, key)
    return watermarked, extracted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="configs/default.json")
    args = parser.parse_args()

    cfg_path = ROOT / args.config
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    seed = int(cfg["seed"])
    random.seed(seed)
    np.random.seed(seed)

    host_path = ROOT / cfg["host_path"]
    watermark_path = ROOT / cfg["watermark_path"]
    ensure_data(host_path, watermark_path)
    host = read_image(host_path)
    watermark = read_image(watermark_path)

    out_fig = ROOT / cfg["outputs"]["figures_dir"]
    out_tab = ROOT / cfg["outputs"]["tables_dir"]
    out_log = ROOT / cfg["outputs"]["logs_dir"]
    out_fig.mkdir(parents=True, exist_ok=True)
    out_tab.mkdir(parents=True, exist_ok=True)
    out_log.mkdir(parents=True, exist_ok=True)

    rho = float(cfg["rho"])
    arnold_iters = int(cfg["arnold_iters"])
    arnold_params = tuple(cfg["arnold_params"])

    watermarked, key, _ = embed_watermark(host, watermark, rho=rho, arnold_iters=arnold_iters, arnold_params=arnold_params)
    extracted = extract_watermark(watermarked, key)
    save_image(out_fig / "host.png", host)
    save_image(out_fig / "watermarked.png", watermarked)
    save_image(out_fig / "watermark_extracted.png", extracted)
    save_triplet_panel(out_fig / "panel_host_wm_extract.png", host, watermarked, extracted)

    rows = []
    attacks = build_attacks()
    for name, fn in attacks.items():
        attacked = fn(watermarked)
        extracted_attack = extract_watermark(attacked, key)
        rows.append(
            {
                "attack": name,
                "psnr_host_vs_watermarked": compute_psnr(host, attacked),
                "ssim_host_vs_watermarked": compute_ssim(host, attacked),
                "nc_wm_vs_extracted": compute_nc(to_gray(watermark), to_gray(extracted_attack)),
            }
        )
        save_image(out_fig / f"{name}_attacked.png", attacked)
        save_image(out_fig / f"{name}_extracted.png", extracted_attack)

    scan_rows = []
    for rho_i in cfg["scan"]["rho_values"]:
        for it_i in cfg["scan"]["arnold_iters"]:
            wm_i, key_i, _ = embed_watermark(host, watermark, rho=float(rho_i), arnold_iters=int(it_i), arnold_params=arnold_params)
            ex_i = extract_watermark(wm_i, key_i)
            scan_rows.append(
                {
                    "rho": rho_i,
                    "arnold_iters": it_i,
                    "psnr": compute_psnr(host, wm_i),
                    "ssim": compute_ssim(host, wm_i),
                    "nc": compute_nc(to_gray(watermark), to_gray(ex_i)),
                }
            )

    with (out_tab / "metrics_attack.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    with (out_tab / "metrics_scan.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(scan_rows[0].keys()))
        writer.writeheader()
        writer.writerows(scan_rows)

    best = sorted(scan_rows, key=lambda x: (-x["nc"], -x["ssim"], -x["psnr"]))[0]
    summary = {
        "config_used": cfg,
        "no_attack_metrics": rows[0],
        "best_scan_config": best,
        "paper_target_trend": {"psnr": ">=35", "ssim": "close_to_1", "nc": "close_to_1"},
    }
    (out_log / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Reproduction finished.")
    print(json.dumps(summary["no_attack_metrics"], ensure_ascii=False, indent=2))
    print(json.dumps({"best_scan_config": best}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
