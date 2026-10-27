"""Registo offline das features da imagem submetida a /inference-grayscale.

Reutiliza a mesma extração da camada 1 do corpus (`image_extract`), mas grava
noutro diretório — o log de pedidos — para agregação/comparação futuras.
Não é um endpoint de histograma de imagem avulsa para o cliente.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PIL.Image import Image as PILImage

from image_extract import extract_image_features

REQUEST_FEATURES_DIR = Path("request_features")


def log_grayscale_submission(
    image: PILImage,
    features_dir: Path = REQUEST_FEATURES_DIR,
) -> Path:
    """Extrai L/R/G/B (+ média de L) da imagem *antes* da conversão a cinza."""
    payload = extract_image_features(image)
    payload["logged_at"] = datetime.now(timezone.utc).isoformat()
    payload["endpoint"] = "grayscale"
    features_dir.mkdir(parents=True, exist_ok=True)
    name = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{uuid4().hex[:8]}.json"
    out = features_dir / name
    out.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return out
