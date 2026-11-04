"""Ban the mass-stamped «Conclusão (autoavaliação)» pattern across lesson READMEs."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

BANNED_EXACT = (
    "## Conclusão (autoavaliação)",
    "Marque **Sim** ou **Não** sozinho",
)

# Vague rows from the 2026-11-04 bulk CONCLUSIONS= script (Remote Progress Analysis).
BANNED_SUBSTRINGS = (
    "se a receita da pasta o permitir",
    "conforme a pasta descreve",
    "`just test` (se houver)",
    "sem olhar o texto",
    "CONCLUSIONS = {",
)


def _lesson_readmes() -> list[Path]:
    return sorted(REPO.glob("[0-9][0-9][0-9]_*/README.md"))


def test_no_conclusao_autoavaliacao_heading() -> None:
    hits: list[str] = []
    for path in _lesson_readmes():
        text = path.read_text(encoding="utf-8")
        for needle in BANNED_EXACT:
            if needle in text:
                hits.append(f"{path.relative_to(REPO)}: {needle!r}")
    assert not hits, "stamp ban:\n" + "\n".join(hits)


def test_no_bulk_stamp_vague_rows() -> None:
    hits: list[str] = []
    for path in _lesson_readmes():
        text = path.read_text(encoding="utf-8")
        for needle in BANNED_SUBSTRINGS:
            if needle in text:
                hits.append(f"{path.relative_to(REPO)}: {needle!r}")
    assert not hits, "vague stamp rows:\n" + "\n".join(hits)
