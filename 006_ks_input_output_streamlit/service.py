import bentoml
from PIL.Image import Image as PILImage

from grayscale_model import load_grayscale_model, load_grayscale_shifted_model
from image_types import ImageInput, Positive
from request_log import log_grayscale_pair
from PIL import ImageFilter


@bentoml.service(resources={"cpu": "1"})
class ImageProcessor:
    def __init__(self) -> None:
        self._grayscale_model = load_grayscale_model()
        self._shifted_model = load_grayscale_shifted_model()

    @bentoml.api(route="/inference-blur")
    def inference_blur(self, image: ImageInput, radius: float = 1.0) -> PILImage:
        return image.filter(ImageFilter.GaussianBlur(radius))

    @bentoml.api(route="/inference-grayscale")
    def inference_grayscale(self, image: ImageInput) -> PILImage:
        out = self._grayscale_model(image)
        log_grayscale_pair(image, out, endpoint="grayscale")
        return out

    @bentoml.api(route="/inference-grayscale-shifted")
    def inference_grayscale_shifted(self, image: ImageInput) -> PILImage:
        out = self._shifted_model(image)
        log_grayscale_pair(image, out, endpoint="grayscale-shifted")
        return out

    @bentoml.api(route="/inference-resize")
    def inference_resize(
        self, image: ImageInput, width: Positive = 256, height: Positive = 256
    ) -> PILImage:
        return image.resize((width, height))
