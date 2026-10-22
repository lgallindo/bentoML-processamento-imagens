"""Gera ilustrações didácticas do pipeline de features → illustrations/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "illustrations"
SAMPLE = ROOT / "samples" / "cesar-fachada-1.webp"


def main() -> int:
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 1) Pipeline camadas ---
    fig, ax = plt.subplots(figsize=(10.5, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.3, 1.0, 1.8, 1.2, "samples/\ntrain_*.jpg", "#dbeafe"),
        (2.5, 1.0, 2.0, 1.2, "Camada 1\nimage_extract\nfeatures/*.json", "#fef3c7"),
        (5.0, 1.0, 2.2, 1.2, "Camada 2\ncorpus_stats\ncorpus_stats.json", "#dcfce7"),
        (7.7, 1.0, 2.0, 1.2, "HTTP\n/monitor-\nhistogram-corpus-*", "#ede9fe"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2)
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=3)
    for x0, x1 in [(2.1, 2.5), (4.5, 5.0), (7.2, 7.7)]:
        ax.annotate(
            "",
            xy=(x1, 1.6),
            xytext=(x0, 1.6),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.8),
            zorder=1,
        )
    ax.set_title("Offline (camadas 1–2) alimenta o relatório HTTP — a API não reabre as fotos")
    fig.savefig(OUT / "01_pipeline_camadas.png", dpi=160)
    plt.close(fig)

    # --- 2) Canais LRGB ---
    img = Image.open(SAMPLE).convert("RGB")
    img_small = img.resize((180, 120))
    arr = np.asarray(img_small)
    L = np.asarray(img_small.convert("L"))
    fig, axes = plt.subplots(1, 5, figsize=(11, 2.8), constrained_layout=True)
    axes[0].imshow(arr)
    axes[0].set_title("RGB original")
    axes[0].axis("off")
    axes[1].imshow(L, cmap="gray", vmin=0, vmax=255)
    axes[1].set_title("L (luminância)")
    axes[1].axis("off")
    for i, (name, plane, cmap) in enumerate(
        [("R", arr[:, :, 0], "Reds"), ("G", arr[:, :, 1], "Greens"), ("B", arr[:, :, 2], "Blues")],
        start=2,
    ):
        axes[i].imshow(plane, cmap=cmap, vmin=0, vmax=255)
        axes[i].set_title(name)
        axes[i].axis("off")
    fig.suptitle("Quatro mapas de intensidade derivados da mesma fotografia", fontsize=12)
    fig.savefig(OUT / "02_canais_LRGB.png", dpi=160)
    plt.close(fig)

    # --- 3) Histograma L + luminance_mean ---
    from image_extract import extract_image_features

    full = Image.open(SAMPLE)
    full.load()
    feat = extract_image_features(full)
    counts = np.array(feat["histograms"]["L"], dtype=float)
    mean = feat["luminance_mean"]
    xs = np.arange(256)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), constrained_layout=True)
    axes[0].imshow(np.asarray(full.convert("L")), cmap="gray")
    axes[0].set_title("Canal L da imagem de exemplo")
    axes[0].axis("off")
    axes[1].bar(xs, counts, width=1.0, color="#4a6fa5", linewidth=0)
    axes[1].axvline(mean, color="#c45c26", linewidth=2.0, label=f"luminance_mean ≈ {mean:.1f}")
    axes[1].set_xlim(0, 255)
    axes[1].set_xlabel("nível (0…255)")
    axes[1].set_ylabel("contagem de píxeis")
    axes[1].set_title("Histograma de L e média ponderada")
    axes[1].legend(loc="upper right", fontsize=9)
    fig.savefig(OUT / "03_histograma_luminance_mean.png", dpi=160)
    plt.close(fig)

    # --- 4) Tutorial flow ---
    fig, ax = plt.subplots(figsize=(10.5, 3.0), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    steps = [
        (0.2, "1. Escolha\numa imagem"),
        (2.3, "2. save_image\n_features(...)"),
        (4.6, "3. features/\n<stem>.json"),
        (6.9, "4. Inspecione\nluminance_mean"),
        (8.7, "5. (Opcional)\nincluir no corpus"),
    ]
    for i, (x, label) in enumerate(steps):
        ax.add_patch(
            plt.Rectangle((x, 0.9), 1.7, 1.3, facecolor="#f1f5f9", edgecolor="#334155", linewidth=1.4)
        )
        ax.text(x + 0.85, 1.55, label, ha="center", va="center", fontsize=9)
        if i < len(steps) - 1:
            ax.annotate(
                "",
                xy=(steps[i + 1][0], 1.55),
                xytext=(x + 1.7, 1.55),
                arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
            )
    ax.set_title("Tutorial: de uma foto qualquer ao JSON de características")
    fig.savefig(OUT / "04_tutorial_uma_imagem.png", dpi=160)
    plt.close(fig)

    print(f"ilustrações em {OUT}")
    for p in sorted(OUT.glob("*.png")):
        print(p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
