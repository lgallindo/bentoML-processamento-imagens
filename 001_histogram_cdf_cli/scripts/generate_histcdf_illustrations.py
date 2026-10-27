"""Gera ilustrações didácticas de histograma e CDF em illustrations/."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "illustrations"

# Exemplo canónico da aula
VALUES = np.array([1.0, 2.0, 2.0, 5.0])
BINS = 4
COUNTS = np.array([1, 2, 0, 1])
EDGES = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
CDF = np.array([0.25, 0.75, 0.75, 1.0])
CENTERS = 0.5 * (EDGES[:-1] + EDGES[1:])
WIDTHS = np.diff(EDGES)


def _style() -> None:
    sns.set_theme(style="whitegrid", font_scale=1.05)
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
        }
    )


def fig_histograma() -> None:
    """Pontos na reta + barras do histograma."""
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 5.2), constrained_layout=True, sharex=True)

    ax0 = axes[0]
    ax0.set_title("Valores na reta: [1, 2, 2, 5] (dois pontos em x = 2)")
    # Pequeno deslocamento vertical para os dois “2” não se sobreporem
    y_offsets = np.array([0.0, 0.12, -0.12, 0.0])
    ax0.scatter(VALUES, y_offsets, s=120, color="#4c72b0", zorder=3)
    for v, y in zip(VALUES, y_offsets, strict=True):
        ax0.annotate(f"{v:g}", (v, y), textcoords="offset points", xytext=(0, 12), ha="center")
    ax0.axhline(0, color="#888", linewidth=1)
    ax0.set_ylim(-0.55, 0.7)
    ax0.set_yticks([])
    ax0.set_xlabel("valor")

    ax1 = axes[1]
    ax1.set_title("Histograma: contagens por bin (bins = 4, intervalo [1, 5])")
    ax1.bar(CENTERS, COUNTS, width=WIDTHS * 0.9, color="#4c72b0", edgecolor="#222", align="center")
    for c, h in zip(CENTERS, COUNTS, strict=True):
        ax1.annotate(str(int(h)), (c, h), textcoords="offset points", xytext=(0, 4), ha="center")
    for e in EDGES:
        ax1.axvline(e, color="#aaa", linestyle=":", linewidth=1)
    ax1.set_xticks(EDGES)
    ax1.set_xlabel("eixo (bordas dos bins)")
    ax1.set_ylabel("contagem")
    ax1.set_ylim(0, 2.6)

    fig.savefig(OUT / "01_o_que_e_histograma.png", dpi=160)
    plt.close(fig)


def fig_cdf() -> None:
    """CDF em degrau com anotações das frações."""
    fig, ax = plt.subplots(figsize=(8.0, 4.2), constrained_layout=True)
    # Degrau pós-bin: após atravessar o bin i, a CDF vale cdf[i]
    xs = np.concatenate([[EDGES[0]], EDGES[1:]])
    ys = np.concatenate([[0.0], CDF])
    ax.step(xs, ys, where="post", color="#c44e52", linewidth=2.4)
    ax.scatter(EDGES[1:], CDF, color="#c44e52", zorder=3, s=50)
    for x, y in zip(EDGES[1:], CDF, strict=True):
        ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(6, 6), ha="left")
    ax.axhline(0, color="#999", linewidth=0.8)
    ax.axhline(1, color="#999", linewidth=0.8, linestyle="--")
    ax.set_ylim(-0.05, 1.12)
    ax.set_xlim(0.8, 5.4)
    ax.set_xlabel("valor (após percorrer os bins até aqui)")
    ax.set_ylabel("F — fração acumulada")
    ax.set_title("CDF empírica: F(i) = (soma das contagens até o bin i) / n")
    fig.savefig(OUT / "02_o_que_e_cdf.png", dpi=160)
    plt.close(fig)


def fig_hist_para_cdf() -> None:
    """Lado a lado: barras → acumulação normalizada."""
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.8), constrained_layout=True)

    ax0 = axes[0]
    ax0.bar(np.arange(4), COUNTS, color="#4c72b0", edgecolor="#222", width=0.75)
    ax0.set_xticks(np.arange(4), [f"bin {i}" for i in range(4)])
    ax0.set_ylabel("contagem")
    ax0.set_title("Histograma: counts = [1, 2, 0, 1]")
    ax0.set_ylim(0, 2.6)
    for i, h in enumerate(COUNTS):
        ax0.annotate(str(int(h)), (i, h), textcoords="offset points", xytext=(0, 4), ha="center")

    ax1 = axes[1]
    running = np.cumsum(COUNTS)
    ax1.plot(np.arange(4), running / running[-1], "o-", color="#c44e52", linewidth=2.2, markersize=8)
    for i, (r, f) in enumerate(zip(running, CDF, strict=True)):
        ax1.annotate(
            f"{int(r)}/{int(running[-1])} = {f:.2f}",
            (i, f),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
        )
    ax1.set_xticks(np.arange(4), [f"bin {i}" for i in range(4)])
    ax1.set_ylabel("CDF")
    ax1.set_ylim(-0.05, 1.2)
    ax1.set_title("CDF: acumulado / total")
    ax1.axhline(1, color="#999", linestyle="--", linewidth=0.8)

    fig.savefig(OUT / "03_histograma_para_cdf.png", dpi=160)
    plt.close(fig)


def fig_tabela_passos() -> None:
    """Tabela visual dos passos de acumulação."""
    fig, ax = plt.subplots(figsize=(8.5, 3.2), constrained_layout=True)
    ax.axis("off")
    ax.set_title("Passo a passo: de counts para cdf (n = 4)", pad=12)

    cell = [
        ["bin", "count", "acumulado", "cdf = acumulado / n"],
        ["0", "1", "1", "1/4 = 0,25"],
        ["1", "2", "1+2 = 3", "3/4 = 0,75"],
        ["2", "0", "3+0 = 3", "3/4 = 0,75"],
        ["3", "1", "3+1 = 4", "4/4 = 1,00"],
    ]
    table = ax.table(
        cellText=cell,
        loc="center",
        cellLoc="center",
        colWidths=[0.12, 0.14, 0.28, 0.36],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.15, 1.7)
    for (row, col), cell_obj in table.get_celld().items():
        if row == 0:
            cell_obj.set_facecolor("#4c72b0")
            cell_obj.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell_obj.set_facecolor("#f3f6fb")
        else:
            cell_obj.set_facecolor("#ffffff")

    fig.savefig(OUT / "04_passos_acumulacao.png", dpi=160)
    plt.close(fig)


def _normal_cdf(x: np.ndarray) -> np.ndarray:
    """CDF da Normal(0,1) via ``math.erf`` (sem SciPy)."""
    from math import erf, sqrt

    scale = sqrt(2.0)
    return np.array([0.5 * (1.0 + erf(float(v) / scale)) for v in x])


def fig_cdf_sigmoid() -> None:
    """Histograma em sino + CDF empírica em S (amostra Normal)."""
    rng = np.random.default_rng(0)
    sample = rng.normal(loc=0.0, scale=1.0, size=5000)
    bins = 40
    lo, hi = -4.0, 4.0
    counts, edges = np.histogram(sample, bins=bins, range=(lo, hi))
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = np.diff(edges)
    empiric = np.cumsum(counts) / counts.sum()

    x_smooth = np.linspace(lo, hi, 400)
    F_theory = _normal_cdf(x_smooth)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), constrained_layout=True)

    ax0 = axes[0]
    ax0.bar(
        centers,
        counts,
        width=widths * 0.95,
        color="#4c72b0",
        edgecolor="#222",
        linewidth=0.3,
        align="center",
    )
    ax0.set_title("Densidade aproximada: amostra Normal(0, 1), n = 5000")
    ax0.set_xlabel("valor")
    ax0.set_ylabel("contagem")
    ax0.set_xlim(lo, hi)

    ax1 = axes[1]
    ax1.step(edges[1:], empiric, where="post", color="#c44e52", linewidth=2.2, label="CDF empírica")
    ax1.plot(x_smooth, F_theory, color="#55a868", linewidth=2.0, linestyle="--", label="CDF teórica N(0,1)")
    ax1.axhline(0, color="#999", linewidth=0.8)
    ax1.axhline(1, color="#999", linewidth=0.8, linestyle=":")
    ax1.set_ylim(-0.05, 1.12)
    ax1.set_xlim(lo, hi)
    ax1.set_xlabel("valor")
    ax1.set_ylabel("F — fração acumulada")
    ax1.set_title("Forma em S: massa no meio → subida íngreme no centro")
    ax1.legend(loc="lower right", frameon=True)

    fig.savefig(OUT / "05_cdf_sigmoid.png", dpi=160)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    fig_histograma()
    fig_cdf()
    fig_hist_para_cdf()
    fig_tabela_passos()
    fig_cdf_sigmoid()
    print(f"ilustrações em {OUT}")
    for path in sorted(OUT.glob("*.png")):
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
