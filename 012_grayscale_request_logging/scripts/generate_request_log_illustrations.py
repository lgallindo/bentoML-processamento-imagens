"""Gera ilustrações didácticas do log em /inference-grayscale → illustrations/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "illustrations"


def main() -> int:
    import matplotlib.pyplot as plt

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 1) Log antes do cinza ---
    fig, ax = plt.subplots(figsize=(10.5, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, 1.0, 1.8, 1.2, "Upload\ncor LRGB", "#dbeafe"),
        (2.4, 1.0, 2.2, 1.2, "log_grayscale\n_submission", "#fef3c7"),
        (5.0, 0.3, 2.0, 1.0, "request_features\n/*.json", "#fce7f3"),
        (5.0, 1.8, 2.0, 1.0, "modelo\npicklable L", "#dcfce7"),
        (7.6, 1.0, 2.0, 1.2, "PNG\ncinza", "#ede9fe"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=3)
    ax.annotate(
        "",
        xy=(2.4, 1.6),
        xytext=(2.0, 1.6),
        arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
    )
    ax.annotate(
        "",
        xy=(5.0, 0.8),
        xytext=(4.6, 1.3),
        arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
    )
    ax.annotate(
        "",
        xy=(5.0, 2.3),
        xytext=(4.6, 1.9),
        arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
    )
    ax.annotate(
        "",
        xy=(7.6, 1.6),
        xytext=(7.0, 2.3),
        arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
    )
    ax.set_title("O registro corre antes da conversão a cinza")
    fig.savefig(OUT / "01_log_before_grayscale.png", dpi=160)
    plt.close(fig)

    # --- 2) Esquema do JSON ---
    fig, ax = plt.subplots(figsize=(8.5, 4.8), constrained_layout=True)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    schema = (
        "{\n"
        '  "bins": 256,\n'
        '  "luminance_mean": 142.3,\n'
        '  "histograms": {\n'
        '    "L": […256 contagens…],\n'
        '    "R": […], "G": […], "B": […]\n'
        "  },\n"
        '  "logged_at": "2026-10-22T13:00:00+00:00",\n'
        '  "endpoint": "grayscale"\n'
        "}"
    )
    ax.text(
        0.5,
        9.2,
        "request_features/<timestamp>_<id>.json",
        fontsize=12,
        fontweight="bold",
        va="top",
    )
    ax.text(0.5, 8.4, schema, family="monospace", fontsize=11, va="top")
    ax.set_title("Campos gravados por pedido")
    fig.savefig(OUT / "02_request_features_schema.png", dpi=160)
    plt.close(fig)

    # --- 3) Grayscale regista; blur não ---
    fig, ax = plt.subplots(figsize=(9.5, 3.4), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    ax.add_patch(
        plt.Rectangle((0.3, 1.6), 4.2, 1.2, facecolor="#dcfce7", edgecolor="#166534", lw=1.5)
    )
    ax.text(
        2.4,
        2.2,
        "/inference-grayscale\n→ novo JSON em request_features/",
        ha="center",
        va="center",
        fontsize=11,
    )
    ax.add_patch(
        plt.Rectangle((5.3, 1.6), 4.2, 1.2, facecolor="#fee2e2", edgecolor="#991b1b", lw=1.5)
    )
    ax.text(
        7.4,
        2.2,
        "/inference-blur (e resize)\n→ sem arquivo novo",
        ha="center",
        va="center",
        fontsize=11,
    )
    ax.set_title("Só o caminho grayscale escreve o log")
    fig.savefig(OUT / "03_blur_skips_log.png", dpi=160)
    plt.close(fig)

    print(f"wrote illustrations under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
