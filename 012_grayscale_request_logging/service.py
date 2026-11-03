import bentoml
from PIL import ImageFilter
from PIL.Image import Image as PILImage

from corpus_report import (
    report_histogram_csv,
    report_histogram_image,
    report_histogram_json,
)
from grayscale_model import load_grayscale_model
from histogram import DEFAULT_BINS
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

    @bentoml.api(route="/monitor-histogram-corpus-json")
    def monitor_histogram_corpus_json(
        self,
        channel: str = "L",
        bins: Positive = DEFAULT_BINS,
    ) -> dict:
        return report_histogram_json(channel=channel, bins=bins)

    @bentoml.api(route="/monitor-histogram-corpus-csv")
    def monitor_histogram_corpus_csv(
        self,
        channel: str = "L",
        bins: Positive = DEFAULT_BINS,
    ) -> str:
        return report_histogram_csv(channel=channel, bins=bins)

    @bentoml.api(route="/monitor-histogram-corpus-image")
    def monitor_histogram_corpus_image(
        self,
        channel: str = "L",
        bins: Positive = DEFAULT_BINS,
        width: Positive = 640,
        height: Positive = 360,
        include_cdf: bool = True,
    ) -> PILImage:
        return report_histogram_image(
            channel=channel,
            bins=bins,
            width=width,
            height=height,
            include_cdf=include_cdf,
        )
