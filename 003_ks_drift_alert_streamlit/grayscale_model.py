"""Modelo BentoML picklable: Pillow convert(\"L\") sem pesos neurais.

Pré-condições: BentoML model store acessível para save/load.

Fluxo::

    GrayscaleModel.__call__ ──► image.convert(\"L\")
    save_grayscale_model ──► tag ──► load_grayscale_model

Saídas principais: save_grayscale_model, load_grayscale_model.
"""

from __future__ import annotations

import bentoml.picklable_model as picklable_model
from PIL.Image import Image as PILImage

MODEL_NAME = "image-grayscale"


class GrayscaleModel:
    def __call__(self, image: PILImage) -> PILImage:
        return image.convert("L")


def save_grayscale_model(name: str = MODEL_NAME) -> str:
    tag = picklable_model.save_model(
        name,
        GrayscaleModel(),
        signatures={"__call__": {"batchable": False}},
        metadata={
            "lesson": "003_ks_drift_alert_streamlit",
            "algorithm": "pillow.convert.L",
        },
    )
    return str(tag)


def load_grayscale_model(tag: str = f"{MODEL_NAME}:latest"):
    return picklable_model.load_model(tag)
