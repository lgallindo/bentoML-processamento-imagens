from typing import Annotated

import bentoml
from PIL import Image, ImageFilter
from PIL.Image import Image as PILImage
from pydantic import Field, WrapValidator


def _decode(value, handler):
    # PIL levanta UnidentifiedImageError (um OSError), que o pydantic nao
    # converte em erro de validacao: vira 500. Reempacota como ValueError -> 400.
    try:
        return handler(value)
    except OSError as exc:
        raise ValueError("arquivo enviado nao e uma imagem valida") from exc


ImageInput = Annotated[PILImage, WrapValidator(_decode)]
Positive = Annotated[int, Field(gt=0)]


@bentoml.service(resources={"cpu": "1"})
class ImageProcessor:

    @bentoml.api
    def blur(self, image: ImageInput, radius: float = 4.0) -> PILImage:
        return image.filter(ImageFilter.GaussianBlur(radius))

    @bentoml.api
    def grayscale(self, image: ImageInput) -> PILImage:
        return image.convert("L")

    @bentoml.api
    def resize(self, image: ImageInput, width: Positive = 256, height: Positive = 256) -> PILImage:
        return image.resize((width, height))
