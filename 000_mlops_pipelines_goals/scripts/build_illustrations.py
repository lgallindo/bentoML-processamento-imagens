#!/usr/bin/env python3
"""Build classroom figures for lesson 000 (show assets)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATIONS = ROOT / "illustrations"
MAX_BYTES = 2 * 1024 * 1024

RUNTIME_LABEL = "Runtime (BentoML)"

GOAL_COLUMNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Saúde do servidor",
        ("raiz /metrics", "004_prometheus_histcdf_streamlit"),
    ),
    (
        "Drift de dados",
        (
            "003_ks_drift_alert_streamlit",
            "010_corpus_histograms_model",
            "020_grayscale_request_logging",
            "030_request_log_histograms",
            "040_ks_production_vs_corpus",
        ),
    ),
    (
        "Detecção de anomalias",
        (
            "005_ks_anomaly_detection_streamlit",
            "004_prometheus_histcdf_streamlit (métricas)",
        ),
    ),
)

ANOMALY_BACKLOG_CHIP = "005_ks_anomaly_detection_streamlit"

REMASTER = ILLUSTRATIONS / "src" / "pipelines-remaster.jpg"
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


def _pipelines_source() -> Path:
    if REMASTER.is_file():
        return REMASTER
    if MUNDO_VEIO.is_file():
        return MUNDO_VEIO
    raise SystemExit(
        f"missing pipelines source (tried {REMASTER} and {MUNDO_VEIO})"
    )


def _overlay_runtime_label(im: Image.Image) -> None:
    """Always paint RUNTIME_LABEL near the OCI / runtime mark (contract)."""
    draw = ImageDraw.Draw(im)
    font = _font(max(28, im.width // 48))
    pad_x, pad_y = 18, 12
    bbox = draw.textbbox((0, 0), RUNTIME_LABEL, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Heuristic: middle tier, slightly right of center (OCI on the remaster).
    x0 = int(im.width * 0.38)
    y0 = int(im.height * 0.48)
    x1 = x0 + tw + 2 * pad_x
    y1 = y0 + th + 2 * pad_y
    draw.rounded_rectangle(
        (x0, y0, x1, y1),
        radius=14,
        fill=(255, 255, 255),
        outline=(14, 165, 233),
        width=3,
    )
    draw.text(
        (x0 + pad_x, y0 + pad_y),
        RUNTIME_LABEL,
        fill=(15, 23, 42),
        font=font,
    )


def build_pipelines(src: Path, dest: Path) -> None:
    im = Image.open(src).convert("RGB")
    max_w = 1800
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.Resampling.LANCZOS)

    _overlay_runtime_label(im)

    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, format="WEBP", quality=82, method=6)
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
        draw.rounded_rectangle(
            box, radius=24, fill=(255, 255, 255), outline=color, width=4
        )
        draw.rectangle((x0, y0, x1, y0 + 14), fill=color)
        nb = draw.textbbox((0, 0), name, font=box_font)
        nx = x0 + (x1 - x0 - (nb[2] - nb[0])) // 2
        draw.text((nx, y0 + 70), name, fill=(15, 23, 42), font=box_font)
        rb = draw.textbbox((0, 0), role, font=role_font)
        rx = x0 + (x1 - x0 - (rb[2] - rb[0])) // 2
        draw.text((rx, y0 + 140), role, fill=(51, 65, 85), font=role_font)

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


def build_goals_lessons_map(dest: Path) -> None:
    width, height = 1600, 720
    im = Image.new("RGB", (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(im)
    title_font = _font(34)
    head_font = _font(26)
    body_font = _font(20)

    draw.text(
        (40, 24),
        "Objetivos finais → pastas da série",
        fill=(15, 23, 42),
        font=title_font,
    )

    colors = ((14, 165, 233), (234, 88, 12), (242, 73, 92))
    gap = 36
    col_w = (width - 80 - 2 * gap) // 3
    top = 100
    bottom = height - 40

    for i, ((title, lines), color) in enumerate(zip(GOAL_COLUMNS, colors, strict=True)):
        x0 = 40 + i * (col_w + gap)
        x1 = x0 + col_w
        draw.rounded_rectangle(
            (x0, top, x1, bottom),
            radius=20,
            fill=(255, 255, 255),
            outline=color,
            width=4,
        )
        draw.rectangle((x0, top, x1, top + 12), fill=color)
        tb = draw.textbbox((0, 0), title, font=head_font)
        tx = x0 + (col_w - (tb[2] - tb[0])) // 2
        draw.text((tx, top + 36), title, fill=(15, 23, 42), font=head_font)

        y = top + 90
        for line in lines:
            chip = line
            cb = draw.textbbox((0, 0), chip, font=body_font)
            cw = cb[2] - cb[0] + 24
            ch = cb[3] - cb[1] + 16
            cx = x0 + (col_w - cw) // 2
            draw.rounded_rectangle(
                (cx, y, cx + cw, y + ch),
                radius=10,
                fill=(241, 245, 249),
                outline=(148, 163, 184),
                width=1,
            )
            draw.text(
                (cx + 12, y + 8),
                chip,
                fill=(51, 65, 85),
                font=body_font,
            )
            y += ch + 14

    # Ensure backlog chip constant is what we drew for anomalias column.
    assert ANOMALY_BACKLOG_CHIP in GOAL_COLUMNS[2][1]

    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, format="WEBP", quality=90, method=6)
    size = dest.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"{dest} is {size} bytes (limit {MAX_BYTES})")


def main() -> None:
    pipelines = ILLUSTRATIONS / "pipelines-mlops.webp"
    target = ILLUSTRATIONS / "bentoml-prometheus-grafana.webp"
    goals = ILLUSTRATIONS / "goals-lessons-map.webp"
    src = _pipelines_source()
    build_pipelines(src, pipelines)
    build_target_path(target)
    build_goals_lessons_map(goals)
    print(f"wrote {pipelines} ({pipelines.stat().st_size} bytes) from {src}")
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    print(f"wrote {goals} ({goals.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
