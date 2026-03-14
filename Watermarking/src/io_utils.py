from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def read_image(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image.astype(np.uint8)).save(path)


def save_triplet_panel(path: Path, host: np.ndarray, watermarked: np.ndarray, extracted: np.ndarray) -> None:
    h = max(host.shape[0], watermarked.shape[0], extracted.shape[0])
    w = host.shape[1] + watermarked.shape[1] + extracted.shape[1]
    canvas = Image.new("RGB", (w, h + 36), color=(255, 255, 255))
    x = 0
    for img in [host, watermarked, extracted]:
        pil = Image.fromarray(img.astype(np.uint8))
        canvas.paste(pil, (x, 36))
        x += pil.width
    draw = ImageDraw.Draw(canvas)
    labels = ["Host", "Watermarked", "Extracted WM"]
    x = 0
    widths = [host.shape[1], watermarked.shape[1], extracted.shape[1]]
    for label, ww in zip(labels, widths):
        draw.text((x + 8, 10), label, fill=(0, 0, 0), font=ImageFont.load_default())
        x += ww
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def generate_demo_host(size: int = 512) -> np.ndarray:
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    xx, yy = np.meshgrid(x, y)
    r = 255 * xx
    g = 255 * yy
    b = 255 * (0.6 * xx + 0.4 * yy)
    img = np.stack([r, g, b], axis=-1)
    return np.clip(img, 0, 255).astype(np.uint8)


def generate_demo_watermark(size: int = 64) -> np.ndarray:
    img = Image.new("RGB", (size, size), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.rectangle([6, 6, size - 7, size - 7], outline=(230, 80, 80), width=2)
    draw.ellipse([16, 16, size - 16, size - 16], outline=(80, 220, 120), width=2)
    draw.text((size // 3, size // 2 - 6), "SQ", fill=(80, 160, 240), font=ImageFont.load_default())
    return np.array(img, dtype=np.uint8)
