"""Gera ilustrações didácticas do KS para illustrations/ (requer matplotlib)."""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "illustrations"


def main() -> int:
    import matplotlib.pyplot as plt
    import numpy as np

    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 13,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )

    # --- 1) Histograma → CDF ---
    counts = np.array([2, 5, 8, 5, 2], dtype=float)
    bins = np.arange(len(counts))
    total = counts.sum()
    cdf = np.cumsum(counts) / total

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), constrained_layout=True)
    axes[0].bar(bins, counts, color="#4a6fa5", edgecolor="black", width=0.85)
    axes[0].set_xlabel("nível (bin)")
    axes[0].set_ylabel("contagem")
    axes[0].set_title("Histograma (contagens)")
    axes[0].set_xticks(bins)

    axes[1].step(
        np.concatenate([[-0.5], bins + 0.5]),
        np.concatenate([[0.0], cdf]),
        where="post",
        color="#c45c26",
        linewidth=2.2,
    )
    axes[1].scatter(bins + 0.5, cdf, color="#c45c26", zorder=3)
    for i, v in enumerate(cdf):
        axes[1].annotate(f"{v:.2f}", (bins[i] + 0.5, v), textcoords="offset points", xytext=(0, 6), ha="center")
    axes[1].set_ylim(-0.05, 1.08)
    axes[1].axhline(0, color="#999", linewidth=0.8)
    axes[1].axhline(1, color="#999", linewidth=0.8, linestyle="--")
    axes[1].set_xlabel("nível (bin)")
    axes[1].set_ylabel("F(x)")
    axes[1].set_title("CDF empírica (acumulação normalizada)")
    fig.savefig(OUT / "01_histograma_para_cdf.png", dpi=160)
    plt.close(fig)

    # --- 2) Forma em “S” (sigmoidal) típica de intensidades ---
    x = np.linspace(0, 255, 256)
    # mistura de duas “massas” → CDF suave em S
    from math import erf

    def norm_cdf(z: np.ndarray, mu: float, sigma: float) -> np.ndarray:
        return 0.5 * (1.0 + np.vectorize(erf)((z - mu) / (sigma * math.sqrt(2))))

    f = 0.55 * norm_cdf(x, 90, 28) + 0.45 * norm_cdf(x, 170, 35)
    dens = np.gradient(f, x)
    dens = np.maximum(dens, 0)
    dens /= dens.sum()

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.6), constrained_layout=True)
    axes[0].fill_between(x, dens * 8000, color="#4a6fa5", alpha=0.85)
    axes[0].set_title("Densidade empírica (esquema)")
    axes[0].set_xlabel("nível de intensidade")
    axes[0].set_ylabel("densidade (relativa)")
    axes[1].plot(x, f, color="#c45c26", linewidth=2.4)
    axes[1].set_ylim(-0.02, 1.05)
    axes[1].set_title("CDF correspondente — forma em «S»")
    axes[1].set_xlabel("nível de intensidade")
    axes[1].set_ylabel("F(x)")
    axes[1].annotate(
        "sobe rápido\nno miolo",
        xy=(130, 0.55),
        xytext=(20, 0.75),
        arrowprops=dict(arrowstyle="->", color="#333"),
        fontsize=10,
    )
    fig.savefig(OUT / "02_cdf_forma_sigmoidal.png", dpi=160)
    plt.close(fig)

    # --- 3) Duas CDF e D = max |F1−F2| ---
    # Exemplo trabalhado de 4 bins
    c1 = np.array([10, 0, 0, 10], dtype=float)
    c2 = np.array([0, 10, 10, 0], dtype=float)
    f1 = np.cumsum(c1) / c1.sum()
    f2 = np.cumsum(c2) / c2.sum()
    gap = np.abs(f1 - f2)
    i_star = int(np.argmax(gap))
    D = float(gap[i_star])
    xs = np.arange(1, 5)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    ax.step(np.concatenate([[0], xs]), np.concatenate([[0], f1]), where="post", label="F_corpus", color="#2a9d8f", linewidth=2.2)
    ax.step(np.concatenate([[0], xs]), np.concatenate([[0], f2]), where="post", label="F_production", color="#e76f51", linewidth=2.2)
    ax.vlines(xs[i_star], f1[i_star], f2[i_star], colors="#264653", linewidths=2.5)
    ax.scatter([xs[i_star]], [f1[i_star]], color="#2a9d8f", zorder=4)
    ax.scatter([xs[i_star]], [f2[i_star]], color="#e76f51", zorder=4)
    mid = (f1[i_star] + f2[i_star]) / 2
    ax.annotate(
        f"D = {D:.2f}",
        xy=(xs[i_star], mid),
        xytext=(xs[i_star] + 0.55, mid),
        arrowprops=dict(arrowstyle="-", color="#264653"),
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlim(0, 4.8)
    ax.set_ylim(-0.05, 1.08)
    ax.set_xlabel("bin")
    ax.set_ylabel("CDF")
    ax.set_title("Comparação de duas CDF: D = max |F₁ − F₂|")
    ax.legend(loc="lower right")
    fig.savefig(OUT / "03_duas_cdf_e_D.png", dpi=160)
    plt.close(fig)

    # --- 4) Hipóteses ---
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), constrained_layout=True)
    t = np.linspace(0, 1, 200)
    axes[0].plot(t, t**0.9 * 0.15 + (1 - np.exp(-3 * t)), color="#2a9d8f", linewidth=2.5)
    axes[0].plot(t, t**0.9 * 0.15 + (1 - np.exp(-3 * t)), color="#e76f51", linewidth=2.5, linestyle="--", alpha=0.9)
    axes[0].set_title("H₀: F_corpus = F_production")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("F(x)")
    axes[0].text(0.35, 0.25, "mesma lei\n(sobrepostas)", ha="center")
    axes[1].plot(t, 1 - np.exp(-2.2 * t), color="#2a9d8f", linewidth=2.5, label="F_corpus")
    axes[1].plot(t, 1 - np.exp(-4.5 * t), color="#e76f51", linewidth=2.5, label="F_production")
    axes[1].set_title("H₁: as leis diferem")
    axes[1].set_xlabel("x")
    axes[1].legend(loc="lower right")
    fig.savefig(OUT / "04_hipoteses_H0_H1.png", dpi=160)
    plt.close(fig)

    # --- 5) Distribuição assintótica de Kolmogorov (densidade de λ) ---
    # pdf approx via derivative of CDF Q; use series for survival then numerical diff
    lam = np.linspace(0.02, 2.5, 400)

    def kolmogorov_cdf(lmbd: float) -> float:
        # P(K ≤ λ) = 1 − 2 Σ (−1)^{k−1} exp(−2 k² λ²)
        s = 0.0
        for k in range(1, 80):
            s += ((-1) ** (k - 1)) * math.exp(-2.0 * (k * lmbd) ** 2)
        return max(0.0, min(1.0, 1.0 - 2.0 * s))

    cdf_k = np.array([kolmogorov_cdf(float(v)) for v in lam])
    pdf_k = np.gradient(cdf_k, lam)
    pdf_k = np.maximum(pdf_k, 0)

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), constrained_layout=True)
    axes[0].fill_between(lam, pdf_k, color="#4a6fa5", alpha=0.85)
    axes[0].set_title("Lei limite de Kolmogorov (densidade em λ)")
    axes[0].set_xlabel("λ = √n_eff · D  (com correcção fraca)")
    axes[0].set_ylabel("densidade")
    axes[0].axvline(1.36, color="#c45c26", linestyle="--", label="≈ quantil 95%")
    axes[0].legend(fontsize=9)

    # survival Q(λ) = P(K > λ) ≈ 2 Σ (−1)^{k-1} e^{−2k²λ²}
    def survival(lmbd: float) -> float:
        s = 0.0
        for k in range(1, 80):
            s += ((-1) ** (k - 1)) * math.exp(-2.0 * (k * lmbd) ** 2)
        return max(0.0, min(1.0, 2.0 * s))

    surv = np.array([survival(float(v)) for v in lam])
    axes[1].plot(lam, surv, color="#c45c26", linewidth=2.2)
    axes[1].set_title("Função de sobrevivência Q(λ) = P(K > λ)")
    axes[1].set_xlabel("λ")
    axes[1].set_ylabel("p-valor assintótico")
    axes[1].set_ylim(-0.02, 1.05)
    fig.savefig(OUT / "05_distribuicao_assintotica.png", dpi=160)
    plt.close(fig)

    # --- 6) Positividade: F não decresce; D ≥ 0 ---
    fig, ax = plt.subplots(figsize=(7.0, 3.6), constrained_layout=True)
    bad_x = [0, 1, 2, 3, 4]
    bad_y = [0.0, 0.4, 0.3, 0.8, 1.0]  # illegal dip
    good_y = [0.0, 0.25, 0.55, 0.8, 1.0]
    ax.plot(bad_x, bad_y, "o--", color="#e76f51", label="inválida (decresce)")
    ax.plot(bad_x, good_y, "o-", color="#2a9d8f", linewidth=2.2, label="válida (não decresce)")
    ax.annotate(
        "proibido",
        xy=(2, 0.3),
        xytext=(2.6, 0.15),
        arrowprops=dict(arrowstyle="->", color="#e76f51"),
        color="#e76f51",
    )
    ax.set_ylim(-0.05, 1.08)
    ax.set_title("Propriedade: CDF empírica é não decrescente (e D ≥ 0)")
    ax.set_xlabel("bin")
    ax.set_ylabel("F")
    ax.legend(loc="lower right")
    fig.savefig(OUT / "06_cdf_nao_decrescente.png", dpi=160)
    plt.close(fig)

    print(f"ilustrações em {OUT}")
    for path in sorted(OUT.glob("*.png")):
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
