"""Gera ilustrações didácticas Prometheus → hist/CDF → illustrations/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "illustrations"


def main() -> int:
    import matplotlib.pyplot as plt
    import numpy as np

    from plotting import plot_histogram_cdf
    from prom_client import fetch_duration_buckets_from_fixture
    from prom_hist import payload_from_samples
    from promql_compare import compare_quantiles

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 1) Fluxo scrape → app ---
    fig, ax = plt.subplots(figsize=(10.5, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, 1.0, 2.0, 1.2, "Bento raiz\n/metrics", "#dbeafe"),
        (2.6, 1.0, 2.0, 1.2, "Prometheus\nbuckets le", "#fef3c7"),
        (5.0, 1.0, 2.2, 1.2, "App Streamlit\nfixture ou live", "#dcfce7"),
        (7.7, 1.0, 2.0, 1.2, "Tabela +\nhist/CDF +\nquantil", "#ede9fe"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=3)
    for x0, x1 in [(2.2, 2.6), (4.6, 5.0), (7.2, 7.7)]:
        ax.annotate(
            "",
            xy=(x1, 1.6),
            xytext=(x0, 1.6),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
        )
    ax.set_title("Da latência observada ao gráfico no app")
    fig.savefig(OUT / "01_scrape_to_buckets.png", dpi=160)
    plt.close(fig)

    samples = fetch_duration_buckets_from_fixture(endpoint="/grayscale")
    payload = payload_from_samples(samples)

    # --- 2) Cumulativo → densidade (contagens por bin) ---
    les = np.asarray(payload["les"][:-1], dtype=float)  # drop +Inf for plot axis
    cum = np.asarray(payload["cumulative"][:-1], dtype=float)
    counts = np.asarray(payload["counts"], dtype=float)
    edges = np.asarray(payload["edges"], dtype=float)
    centers = 0.5 * (edges[:-1] + edges[1:])

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), constrained_layout=True)
    axes[0].step(les, cum, where="post", color="#4c72b0", linewidth=2)
    axes[0].scatter(les, cum, color="#4c72b0", zorder=3)
    axes[0].set_title("Buckets cumulativos (le)")
    axes[0].set_xlabel("le (s)")
    axes[0].set_ylabel("contagem acumulada")
    axes[0].grid(True, alpha=0.3)

    widths = np.diff(edges)
    axes[1].bar(centers, counts, width=widths * 0.9, color="#55a868", align="center")
    axes[1].set_title("Contagens por bin (diferença)")
    axes[1].set_xlabel("duração (s)")
    axes[1].set_ylabel("contagem")
    axes[1].grid(True, alpha=0.3)
    fig.suptitle("Fixture /grayscale: cumulativo → densidade")
    fig.savefig(OUT / "02_cumulative_to_density.png", dpi=160)
    plt.close(fig)

    # --- 3) Hist+CDF + anotação do p95 Python ---
    fig = plot_histogram_cdf(
        payload["counts"],
        payload["edges"],
        payload["cdf"],
        title="Fixture /grayscale — histograma e CDF",
    )
    cmp = compare_quantiles(
        payload["les"], payload["cumulative"], q=0.95, endpoint="/grayscale"
    )
    py_val = cmp["python"]["value"]
    ax = fig.axes[0]
    ax.axvline(py_val, color="#c44e52", linestyle="--", linewidth=1.5)
    ax.text(
        py_val,
        ax.get_ylim()[1] * 0.92,
        f"p95≈{py_val:.3f}s",
        color="#c44e52",
        ha="left",
        fontsize=10,
    )
    fig.savefig(OUT / "03_python_vs_promql_quantile.png", dpi=160)
    plt.close(fig)

    print(f"wrote illustrations under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
