"""Empacotamento clássico de tons de cinza como modelo BentoML."""

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
            "lesson": "010_corpus_histograms_model",
            "algorithm": "pillow.convert.L",
        },
    )
    return str(tag)


def load_grayscale_model(tag: str = f"{MODEL_NAME}:latest"):
    return picklable_model.load_model(tag)
