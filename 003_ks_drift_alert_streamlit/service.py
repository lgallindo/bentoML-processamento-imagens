"""Serviço BentoML da aula 003: blur, cinza (com log) e resize.

Pré-condições: modelo grayscale gravado (`just save-grayscale-model`).

Fluxo::

    POST /inference-grayscale ──► log_grayscale_submission ──► convert L
    POST /inference-blur|resize ──► Pillow (sem log KS)

Saídas principais: ImageProcessor (rotas BentoML).
"""

import bentoml
from PIL import ImageFilter
from PIL.Image import Image as PILImage

from grayscale_model import load_grayscale_model
from image_types import ImageInput, Positive
from request_log import log_grayscale_submission


@bentoml.service(resources={"cpu": "1"})
class ImageProcessor:
    def __init__(self) -> None:
        self._grayscale_model = load_grayscale_model()

    @bentoml.api(route="/inference-blur")
    def inference_blur(self, image: ImageInput, radius: float = 1.0) -> PILImage:
        return image.filter(ImageFilter.GaussianBlur(radius))

    @bentoml.api(route="/inference-grayscale")
    def inference_grayscale(self, image: ImageInput) -> PILImage:
        log_grayscale_submission(image)
        return self._grayscale_model(image)

    @bentoml.api(route="/inference-resize")
    def inference_resize(
        self, image: ImageInput, width: Positive = 256, height: Positive = 256
    ) -> PILImage:
        return image.resize((width, height))
