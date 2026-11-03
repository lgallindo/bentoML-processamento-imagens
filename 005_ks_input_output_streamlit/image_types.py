from typing import Annotated

from PIL.Image import Image as PILImage
from pydantic import Field

ImageInput = PILImage
Positive = Annotated[int, Field(gt=0)]
