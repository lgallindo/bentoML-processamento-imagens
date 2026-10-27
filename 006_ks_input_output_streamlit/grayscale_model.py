"""Modelos picklable: cinza saudável e cinza com deslocamento de L."""

from __future__ import annotations

import bentoml.picklable_model as picklable_model
from PIL.Image import Image as PILImage

MODEL_NAME = "image-grayscale-006"
SHIFTED_MODEL_NAME = "image-grayscale-shifted-006"
SHIFT_DELTA = 40


class GrayscaleModel:
    def __call__(self, image: PILImage) -> PILImage:
        return image.convert("L")


class GrayscaleShiftedModel:
    """convert("L") e depois soma SHIFT_DELTA em cada pixel (com teto 255)."""

    def __init__(self, delta: int = SHIFT_DELTA) -> None:
        self.delta = int(delta)

    def __call__(self, image: PILImage) -> PILImage:
        gray = image.convert("L")
        delta = self.delta
        return gray.point(lambda p: min(255, p + delta))


def save_grayscale_model(name: str = MODEL_NAME) -> str:
    tag = picklable_model.save_model(
        name,
        GrayscaleModel(),
        signatures={"__call__": {"batchable": False}},
        metadata={
            "lesson": "006_ks_input_output_streamlit",
            "algorithm": "pillow.convert.L",
        },
    )
    return str(tag)


def save_grayscale_shifted_model(name: str = SHIFTED_MODEL_NAME) -> str:
    tag = picklable_model.save_model(
        name,
        GrayscaleShiftedModel(),
        signatures={"__call__": {"batchable": False}},
        metadata={
            "lesson": "006_ks_input_output_streamlit",
            "algorithm": "pillow.convert.L.plus_delta",
            "shift_delta": SHIFT_DELTA,
        },
    )
    return str(tag)


def load_grayscale_model(tag: str = f"{MODEL_NAME}:latest"):
    return picklable_model.load_model(tag)


def load_grayscale_shifted_model(tag: str = f"{SHIFTED_MODEL_NAME}:latest"):
    return picklable_model.load_model(tag)
