#!/usr/bin/env python3
"""Caixa 1 — L (pixel): converte a imagem para tons de cinza.

Executa somente esta caixa. Não calcula histograma, CDF nem alerta.

Uso::

    python scripts/workflow_boxes/box_01_luminancia.py
"""

from __future__ import annotations

from PIL import Image


def luminancia_L(image: Image.Image) -> Image.Image:
    """Devolve a mesma grade de pixels em modo L (0 = preto … 255 = branco).

    Alternativas:
      - média ponderada manual dos canais RGB (fórmula Rec. 601);
      - canal único (R, G ou B) se a pergunta for cor, não brilho.
    Aqui usamos ``convert("L")`` do Pillow, padrão da aula.
    """
    return image.convert("L")


def main() -> int:
    # Imagem sintética 4×4: fácil de inspecionar sem samples/ no disco.
    rgb = Image.new("RGB", (4, 4), (30, 90, 200))
    cinza = luminancia_L(rgb)
    assert cinza.mode == "L"
    assert cinza.size == (4, 4)
    # Um pixel basta para provar que saímos de RGB.
    print(f"mode={cinza.mode} size={cinza.size} L[0,0]={cinza.getpixel((0, 0))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
