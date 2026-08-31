import bentoml
from PIL import Image, ImageFilter
from PIL.Image import Image as PILImage


@bentoml.service(resources={"cpu": "1"})
class ImageProcessor:

    @bentoml.api
    def grayscale(self, image: PILImage) -> PILImage:
        return image.convert("L")

    @bentoml.api
    def blur(self, image: PILImage, radius: float = 4.0) -> PILImage:
        return image.filter(ImageFilter.GaussianBlur(radius))

    @bentoml.api
    def resize(self, image: PILImage, width: int = 256, height: int = 256) -> PILImage:
        return image.resize((width, height))
