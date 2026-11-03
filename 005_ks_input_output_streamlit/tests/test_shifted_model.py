from __future__ import annotations

from PIL import Image

from grayscale_model import SHIFT_DELTA, GrayscaleShiftedModel


def test_shift_adds_delta_and_clamps() -> None:
    model = GrayscaleShiftedModel(SHIFT_DELTA)
    img = Image.new("RGB", (2, 2), (10, 10, 10))
    out = model(img)
    assert out.mode == "L"
    assert out.getpixel((0, 0)) == 10 + SHIFT_DELTA

    bright = Image.new("RGB", (1, 1), (250, 250, 250))
    assert model(bright).getpixel((0, 0)) == 255
