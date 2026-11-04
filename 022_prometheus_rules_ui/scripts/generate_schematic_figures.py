"""Figuras didácticas (esquemáticas) da aula 021 — sausage sob scripts/."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "illustrations"
OUT.mkdir(parents=True, exist_ok=True)


def _box(ax, x, y, w, h, text, fc="#f5f5f5"):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.2,
        edgecolor="#333333",
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, wrap=True)


def workflow_yaml_to_rules() -> None:
    fig, ax = plt.subplots(figsize=(11, 2.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.3, 0.9, 2.0, 1.2, "bentoml.rules.yml\n(record / alert)", "#eef6ff"),
        (2.7, 0.9, 2.0, 1.2, "prometheus.yml\nrule_files:", "#eef6ff"),
        (5.1, 0.9, 2.0, 1.2, "evaluation_interval\nreavalia o grupo", "#fff8e6"),
        (7.5, 0.9, 2.0, 1.2, "UI /rules\nestado + última eval", "#e8f7ee"),
    ]
    for x, y, w, h, text, fc in boxes:
        _box(ax, x, y, w, h, text, fc)
    for x in (2.4, 4.8, 7.2):
        ax.annotate(
            "",
            xy=(x + 0.25, 1.5),
            xytext=(x - 0.15, 1.5),
            arrowprops=dict(arrowstyle="->", color="#444444", lw=1.4),
        )
    ax.set_title("Do arquivo versionado à página Rules", fontsize=12, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "00_yaml_to_rules_workflow.png", dpi=140)
    plt.close(fig)


def rules_vs_graph_vs_alerts() -> None:
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.4)
    ax.axis("off")
    for y, title, body in [
        (2.2, "Graph / Table", "Você digita PromQL.\nResposta pontual."),
        (1.2, "Rules", "O servidor reavalia\nYAML carregado."),
        (0.2, "Alerts", "Só alertas e estado\ninactive/pending/firing."),
    ]:
        _box(ax, 0.4, y, 2.4, 0.9, title, "#f0f0f0")
        ax.text(3.1, y + 0.45, body, va="center", fontsize=10)
    ax.set_title("Três páginas, três intenções", fontsize=12, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "06_rules_vs_graph_vs_alerts.png", dpi=140)
    plt.close(fig)


def main() -> None:
    workflow_yaml_to_rules()
    rules_vs_graph_vs_alerts()
    print(f"wrote figures under {OUT}")


if __name__ == "__main__":
    main()
