"""Testes do manifesto e da política de checksum do corpus."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.download_samples import DEFAULT_COUNT, sha256_bytes, training_url


def test_training_url_is_deterministic() -> None:
    assert training_url(1) == training_url(1)
    assert "bentoml-edu-1" in training_url(1)
    assert training_url(1) != training_url(2)


def test_sha256_roundtrip_on_bytes() -> None:
    payload = b"fixture-image-bytes"
    digest = sha256_bytes(payload)
    assert digest == hashlib.sha256(payload).hexdigest()
    assert len(digest) == 64


def test_manifest_schema_when_present() -> None:
    manifest_path = Path(__file__).resolve().parent.parent / "samples" / "MANIFEST.json"
    if not manifest_path.is_file():
        return
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["count"] >= DEFAULT_COUNT
    assert len(data["images"]) == data["count"]
    for entry in data["images"]:
        assert {"id", "seed", "url", "path", "sha256"} <= set(entry)
        assert entry["path"].startswith("samples/train_")
        assert len(entry["sha256"]) == 64
