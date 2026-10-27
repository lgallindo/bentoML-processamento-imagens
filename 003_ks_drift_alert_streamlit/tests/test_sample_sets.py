"""Referência e lote de controle não compartilham arquivos (anti-leak)."""

from __future__ import annotations

from sample_sets import (
    CONTROL_COUNT,
    CONTROL_OFFSET,
    CORPUS_TAKE,
    caminhos_referencia,
    theme_paths_for_batch,
)


def test_control_paths_disjoint_from_corpus() -> None:
    ref = set(caminhos_referencia())
    control = set(theme_paths_for_batch("control"))
    assert len(ref) == CORPUS_TAKE
    assert len(control) == CONTROL_COUNT
    assert ref.isdisjoint(control)


def test_control_slice_starts_at_offset() -> None:
    from sample_sets import list_image_paths, repo_root

    beaches = list_image_paths(repo_root() / "samples" / "beaches")
    control = theme_paths_for_batch("control")
    assert control[0] == beaches[CONTROL_OFFSET]
    assert control[-1] == beaches[CONTROL_OFFSET + CONTROL_COUNT - 1]
