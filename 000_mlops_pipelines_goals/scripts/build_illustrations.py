#!/usr/bin/env python3
"""Build classroom figures for lesson 000 (show assets)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATIONS = ROOT / "illustrations"
MAX_BYTES = 2 * 1024 * 1024

# Prefer Downloads sources when present; fall back to nothing for CI-less rebuild.
MUNDO_VEIO = Path.home() / "Downloads" / "monitoramento" / "mundo-veio.png"


def _font(size: int) -> ImageFont.ImageFont:
    for name in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ):
        path = Path(name)
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def build_pipelines(src: Path, dest: Path) -> None:
    im = Image.open(src).convert("RGB")
    # Downscale for projector + size budget while keeping readability.
    max_w = 1800
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.Resampling.LANCZOS)

    caption_h = 72
    canvas = Image.new("RGB", (im.width, im.height + caption_h), (248, 250, 252))
    canvas.paste(im, (0, 0))
    draw = ImageDraw.Draw(canvas)
    font = _font(28)
    text = "A máquina virtual / runtime de inferência é gerida pelo BentoML."
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = max(16, (canvas.width - tw) // 2)
    y = im.height + (caption_h - (bbox[3] - bbox[1])) // 2
    draw.text((x, y), text, fill=(15, 23, 42), font=font)

    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, format="WEBP", quality=82, method=6)
    size = dest.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"{dest} is {size} bytes (limit {MAX_BYTES})")


def build_target_path(dest: Path) -> None:
    width, height = 1600, 520
    im = Image.new("RGB", (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(im)
    title_font = _font(36)
    box_font = _font(32)
    role_font = _font(22)

    draw.text(
        (40, 28),
        "Arquitetura-alvo de observabilidade",
        fill=(15, 23, 42),
        font=title_font,
    )

    boxes = [
        ("BentoML", "Expõe /metrics", (40, 140, 420, 360), (14, 165, 233)),
        ("Prometheus", "Coleta, guarda, regras", (590, 140, 970, 360), (234, 88, 12)),
        ("Grafana", "Painéis e alertas", (1140, 140, 1520, 360), (242, 73, 92)),
    ]

    for name, role, box, color in boxes:
        x0, y0, x1, y1 = box
        draw.rounded_rectangle(box, radius=24, fill=(255, 255, 255), outline=color, width=4)
        # accent bar
        draw.rectangle((x0, y0, x1, y0 + 14), fill=color)
        nb = draw.textbbox((0, 0), name, font=box_font)
        nx = x0 + (x1 - x0 - (nb[2] - nb[0])) // 2
        draw.text((nx, y0 + 70), name, fill=(15, 23, 42), font=box_font)
        rb = draw.textbbox((0, 0), role, font=role_font)
        rx = x0 + (x1 - x0 - (rb[2] - rb[0])) // 2
        draw.text((rx, y0 + 140), role, fill=(51, 65, 85), font=role_font)

    # Arrows between boxes
    arrow_y = 250
    for x0, x1 in ((420, 590), (970, 1140)):
        draw.line((x0 + 8, arrow_y, x1 - 8, arrow_y), fill=(15, 23, 42), width=6)
        draw.polygon(
            [
                (x1 - 8, arrow_y),
                (x1 - 28, arrow_y - 14),
                (x1 - 28, arrow_y + 14),
            ],
            fill=(15, 23, 42),
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, format="WEBP", quality=90, method=6)
    size = dest.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"{dest} is {size} bytes (limit {MAX_BYTES})")


def main() -> None:
    pipelines = ILLUSTRATIONS / "pipelines-mlops.webp"
    target = ILLUSTRATIONS / "bentoml-prometheus-grafana.webp"
    if not MUNDO_VEIO.is_file():
        raise SystemExit(f"missing source image: {MUNDO_VEIO}")
    build_pipelines(MUNDO_VEIO, pipelines)
    build_target_path(target)
    print(f"wrote {pipelines} ({pipelines.stat().st_size} bytes)")
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
