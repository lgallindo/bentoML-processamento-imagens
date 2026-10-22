"""Resolve the git repository root (portable across clone paths)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def repo_root() -> Path:
    out = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
    ).strip()
    return Path(out)


def themed_samples(batch: str) -> Path:
    """Return `<repo>/samples/<batch>/` (beaches, forests, balls, demo)."""
    return repo_root() / "samples" / batch
