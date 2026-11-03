"""Referência e lote de controle não compartilham arquivos (anti-leak)."""

from __future__ import annotations

from pathlib import Path

import pytest

from sample_sets import (
    CONTROL_COUNT,
    CONTROL_OFFSET,
    CORPUS_TAKE,
    caminhos_referencia,
    theme_paths_for_batch,
)


def test_repo_root_uses_samples_root_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from sample_sets import repo_root

    samples_root = tmp_path / "lesson-copy"
    (samples_root / "samples").mkdir(parents=True)
    monkeypatch.setenv("SAMPLES_ROOT", str(samples_root))
    assert repo_root() == samples_root.resolve()


def test_repo_root_finds_samples_in_lesson_only_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sample_sets

    lesson = tmp_path / "lesson"
    (lesson / "samples").mkdir(parents=True)
    monkeypatch.delenv("SAMPLES_ROOT", raising=False)
    monkeypatch.setattr(sample_sets, "__file__", str(lesson / "sample_sets.py"))
    assert sample_sets.repo_root() == lesson.resolve()


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
