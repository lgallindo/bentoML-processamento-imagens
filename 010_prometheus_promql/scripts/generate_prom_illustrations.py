"""Gera ilustrações didácticas Prometheus → hist/CDF → illustrations/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "illustrations"


def _write_counter_scrapes_odometer(plt, np) -> None:
    """Odômetro em scrapes sucessivos: absoluto ≠ taxa."""
    times = np.array([0, 15, 30, 45])
    values = np.array([5, 8, 11, 14])
    deltas = np.diff(values)

    fig, ax = plt.subplots(figsize=(10.5, 4.0), constrained_layout=True)
    ax.plot(times, values, color="#4c72b0", linewidth=2, marker="o", markersize=8, zorder=3)
    for t, v in zip(times, values):
        ax.annotate(
            f"{v}",
            xy=(t, v),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=11,
            fontweight="bold",
            color="#1e3a5f",
        )
    for i, d in enumerate(deltas):
        mid_t = 0.5 * (times[i] + times[i + 1])
        mid_v = 0.5 * (values[i] + values[i + 1])
        ax.annotate(
            f"Δ = +{d}",
            xy=(mid_t, mid_v),
            xytext=(0, -22),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            color="#55a868",
        )
    ax.axhline(5, color="#94a3b8", linestyle=":", linewidth=1, alpha=0.8)
    ax.text(
        46,
        5.3,
        "um scrape isolado = odômetro\n(não é velocímetro)",
        fontsize=9,
        color="#64748b",
        va="bottom",
        ha="right",
    )
    ax.set_xlabel("tempo do scrape (s)")
    ax.set_ylabel("valor do contador")
    ax.set_title("Contador em scrapes: absoluto 5 → 8 → 11 → 14; rate exige ≥ 2 pontos")
    ax.set_ylim(0, 18)
    ax.grid(True, alpha=0.3)
    ax.text(
        0.02,
        0.98,
        "rate ≈ Δ / Δt  (só após duas ou mais coletas)",
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        color="#334155",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f1f5f9", edgecolor="#cbd5e1"),
    )
    fig.savefig(OUT / "05_counter_scrapes_odometer.png", dpi=160)
    plt.close(fig)


def _write_counter_reset_rate(plt, np) -> None:
    """Reinício: subtração ingénua negativa vs trechos monótonos."""
    times = np.array([0, 15, 30, 45, 60])
    values = np.array([100, 115, 130, 2, 20])

    fig, ax = plt.subplots(figsize=(10.5, 4.2), constrained_layout=True)
    ax.plot(times[:3], values[:3], color="#4c72b0", linewidth=2, marker="o", zorder=3)
    ax.plot(times[3:], values[3:], color="#4c72b0", linewidth=2, marker="o", zorder=3)
    ax.plot(
        [times[2], times[3]],
        [values[2], values[3]],
        color="#c44e52",
        linewidth=2,
        linestyle="--",
        marker="o",
        zorder=4,
    )
    ax.annotate(
        "reinício\n(resets)",
        xy=(37.5, 66),
        xytext=(42, 90),
        fontsize=10,
        color="#c44e52",
        arrowprops=dict(arrowstyle="->", color="#c44e52"),
    )
    ax.annotate(
        "ingénuo: 20 − 100 = −80\n(absurdo)",
        xy=(60, 20),
        xytext=(48, 45),
        fontsize=9,
        color="#c44e52",
        arrowprops=dict(arrowstyle="->", color="#c44e52", ls=":"),
    )
    ax.annotate(
        "rate/increase:\n+30 + +18 = +48\n(só trechos ↑)",
        xy=(15, 115),
        xytext=(2, 145),
        fontsize=9,
        color="#55a868",
        arrowprops=dict(arrowstyle="->", color="#55a868"),
    )
    ax.fill_between([0, 30], 0, 160, color="#dbeafe", alpha=0.35, label="trecho monótono 1")
    ax.fill_between([45, 60], 0, 160, color="#dcfce7", alpha=0.35, label="trecho monótono 2")
    ax.set_xlabel("tempo do scrape (s)")
    ax.set_ylabel("valor do contador")
    ax.set_title("Reinício do processo: odômetro zera; rate soma só os trechos monótonos")
    ax.set_ylim(0, 160)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    fig.savefig(OUT / "06_counter_reset_rate.png", dpi=160)
    plt.close(fig)


def _write_gauge_in_progress(plt, np) -> None:
    """Gauge em voo: pico curto vs platô alto."""
    times = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120])
    values = np.array([0, 1, 3, 1, 0, 0, 2, 5, 5, 5, 5, 4, 5])

    fig, ax = plt.subplots(figsize=(10.5, 4.2), constrained_layout=True)
    ax.plot(times, values, color="#7c3aed", linewidth=2, marker="o", markersize=6, zorder=3)
    ax.fill_between(times, values, color="#ede9fe", alpha=0.5)
    ax.annotate(
        "pico curto\n(concorrência legítima)",
        xy=(20, 3),
        xytext=(5, 6.5),
        fontsize=9,
        color="#5b21b6",
        arrowprops=dict(arrowstyle="->", color="#5b21b6"),
    )
    ax.axhspan(4.5, 5.5, xmin=0.52, xmax=0.92, facecolor="#fecaca", alpha=0.45, zorder=1)
    ax.annotate(
        "platô alto por minutos\n(saturação / travamento?)",
        xy=(90, 5),
        xytext=(70, 7.2),
        fontsize=9,
        color="#b91c1c",
        arrowprops=dict(arrowstyle="->", color="#b91c1c"),
    )
    ax.set_xlabel("tempo (s)")
    ax.set_ylabel("em voo agora (gauge)")
    ax.set_title("Gauge bentoml_service_request_in_progress: sobe e desce de propósito")
    ax.set_ylim(-0.3, 8.5)
    ax.grid(True, alpha=0.3)
    fig.savefig(OUT / "07_gauge_in_progress.png", dpi=160)
    plt.close(fig)


def _write_legacy_hist_figures(plt, np) -> None:
    """Regenera 01–03 quando plotting/prom_* estão importáveis (aula 015 no path)."""
    lesson_015 = ROOT.parent / "015_prometheus_histcdf_streamlit"
    for path in (ROOT, lesson_015):
        path_s = str(path)
        if path_s not in sys.path:
            sys.path.insert(0, path_s)

    from plotting import plot_histogram_cdf
    from prom_client import fetch_duration_buckets_from_fixture
    from prom_hist import payload_from_samples
    from promql_compare import compare_quantiles

    # --- 1) Fluxo scrape → buckets ---
    fig, ax = plt.subplots(figsize=(10.5, 3.2), constrained_layout=True)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, 1.0, 2.0, 1.2, "Bento raiz\n/metrics", "#dbeafe"),
        (2.6, 1.0, 2.0, 1.2, "Prometheus\nbuckets le", "#fef3c7"),
        (5.0, 1.0, 2.2, 1.2, "Consulta\nfixture ou live", "#dcfce7"),
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
    ax.set_title("Da latência observada ao gráfico")
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


def _write_sample_path_flow(plt) -> None:
    """Caminho da amostra: memória → /metrics → scrape → TSDB → PromQL."""
    fig, ax = plt.subplots(figsize=(11.0, 3.4), constrained_layout=True)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    boxes = [
        (0.15, 1.0, 1.9, 1.4, "BentoML\ncontadores\nem memória", "#dbeafe"),
        (2.25, 1.0, 1.9, 1.4, "GET /metrics\ntexto tipado\n:3000", "#e0e7ff"),
        (4.35, 1.0, 2.0, 1.4, "Prometheus\nscrape ~5 s\nlê o corpo", "#fef3c7"),
        (6.55, 1.0, 2.0, 1.4, "TSDB local\n(série,\ntimestamp, value)", "#dcfce7"),
        (8.75, 1.0, 2.0, 1.4, "PromQL\nlê o TSDB\n(não o vivo)", "#ede9fe"),
    ]
    for x, y, w, h, text, color in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="#334155", linewidth=1.5, zorder=2
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, zorder=3)
    for x0, x1 in [(2.05, 2.25), (4.15, 4.35), (6.35, 6.55), (8.55, 8.75)]:
        ax.annotate(
            "",
            xy=(x1, 1.7),
            xytext=(x0, 1.7),
            arrowprops=dict(arrowstyle="->", color="#334155", lw=1.5),
        )
    ax.text(
        5.5,
        0.35,
        "Navegador em :3000 = /metrics ao vivo; consultas na UI :9090 = TSDB",
        ha="center",
        fontsize=9,
        color="#475569",
    )
    ax.set_title("Caminho de uma amostra: memória → exposição → scrape → TSDB → PromQL")
    fig.savefig(OUT / "08_sample_path_memory_to_promql.png", dpi=160)
    plt.close(fig)


def main() -> int:
    import matplotlib.pyplot as plt
    import numpy as np

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 5–8) Figuras didácticas da §1.2 e §2.1 ---
    _write_counter_scrapes_odometer(plt, np)
    _write_counter_reset_rate(plt, np)
    _write_gauge_in_progress(plt, np)
    _write_sample_path_flow(plt)

    try:
        _write_legacy_hist_figures(plt, np)
    except Exception as exc:  # noqa: BLE001 — regeneração opcional de 01–03
        print(f"aviso: não regenerou 01–03 ({exc}); PNGs existentes preservados")

    print(f"wrote illustrations under {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
