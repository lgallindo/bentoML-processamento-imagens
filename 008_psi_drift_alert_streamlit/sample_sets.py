"""Conjuntos de amostras da aula 008: referência vs lotes (sem overlap no controle).

Pré-condições: `samples/<tema>/` na raiz do repositório Git;
`batch_stats/` materializado por `just build-demo-batches`.

Fluxo::

    beaches ordenadas ──► [:CORPUS_TAKE] = referência
                       ──► [CONTROL_OFFSET:CONTROL_OFFSET+CONTROL_COUNT] = control
    forests/balls ──► tema completo

Saídas principais: caminhos_referencia, theme_paths_for_batch, list_batch_names.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

CORPUS_TAKE = 50
CONTROL_OFFSET = 50
CONTROL_COUNT = 50

LOTE_ROTULO = {
    "control": "Mesmo tema (outro trecho de praias)",
    "forests": "Florestas",
    "balls": "Bolas",
}

# landscapes = aula 007 / contingência mista; beaches = fatia de treino (leak)
LOTES_EXCLUIDOS = frozenset({"landscapes", "beaches"})


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def list_image_paths(folder: Path) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(
            f"pasta de amostras ausente: {folder} "
            "(rode just verify-themed-samples na raiz do repositório)"
        )
    return sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))


def caminhos_referencia() -> list[Path]:
    """Primeiras CORPUS_TAKE praias — mesmo freeze do corpus_stats.json."""
    beaches = list_image_paths(repo_root() / "samples" / "beaches")
    if len(beaches) < CORPUS_TAKE:
        raise FileNotFoundError(
            f"esperadas ≥{CORPUS_TAKE} praias em samples/beaches/; "
            f"encontradas {len(beaches)}"
        )
    return beaches[:CORPUS_TAKE]


def theme_paths_for_batch(name: str) -> list[Path]:
    """Caminhos de amostra do lote — control usa offset disjunto do treino."""
    root = repo_root() / "samples"
    if name == "control":
        beaches = list_image_paths(root / "beaches")
        fim = CONTROL_OFFSET + CONTROL_COUNT
        if len(beaches) < fim:
            raise FileNotFoundError(
                f"controle precisa de ≥{fim} praias; encontradas {len(beaches)} "
                "(rode just verify-themed-samples na raiz)"
            )
        return beaches[CONTROL_OFFSET:fim]
    mapping = {
        "forests": root / "forests",
        "balls": root / "balls",
    }
    folder = mapping.get(name, root / name)
    return list_image_paths(folder)


def rotulo_lote(name: str) -> str:
    return LOTE_ROTULO.get(name, name)


def list_batch_names(batch_stats_dir: Path) -> list[str]:
    if not batch_stats_dir.is_dir():
        raise FileNotFoundError(
            f"pasta de lotes ausente: {batch_stats_dir} "
            "(rode just build-demo-batches nesta aula)"
        )
    names = sorted(
        p.stem
        for p in batch_stats_dir.glob("*.json")
        if p.stem not in LOTES_EXCLUIDOS and "+" not in p.stem
    )
    if not names:
        raise FileNotFoundError(
            f"nenhum JSON de lote em {batch_stats_dir} "
            "(rode just build-demo-batches nesta aula)"
        )
    return names
