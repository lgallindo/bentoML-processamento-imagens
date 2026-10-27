"""Aliases de tipos para a API BentoML desta aula.

Pré-condições: nenhuma (só anotações).

Fluxo::

    ImageInput / Positive ──► usados nas assinaturas de service.py

Saídas principais: ImageInput, Positive.
"""

from typing import Annotated

from PIL.Image import Image as PILImage
from pydantic import Field

ImageInput = PILImage
Positive = Annotated[int, Field(gt=0)]
