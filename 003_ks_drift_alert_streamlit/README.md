# Lição 003 — Alerta KS de drift (BentoML + Streamlit)

## Variável: **L** (luminância de cada pixel)

Tudo o que o Streamlit desenha (histograma, CDF, estatística de
Kolmogorov–Smirnov) é a **distribuição de L sobre os pixels** de cada
conjunto de imagens.

| Símbolo | O que é |
| :--- | :--- |
| **L** | Valor de cinza do pixel após `Image.convert("L")`: inteiro **0** (preto) … **255** (branco) |
| Unidade da amostra | **Pixel** (não a imagem inteira; RGB por canal fica de fora deste KS) |
| Comparação | distribuição de L na **referência** vs distribuição de L no **lote** |

### Como extrair L de uma imagem (prova de conceito)

Mínimo com Pillow — sem defensiva:

```python
from PIL import Image

img = Image.open("foto.jpg").convert("L")  # cada pixel → L ∈ {0, …, 255}
contagens = img.histogram()               # 256 faixas: quantos pixels têm cada L
# Some `contagens` de várias imagens → histograma do conjunto → CDF → KS.
```

No serviço da lição, o mesmo L entra no JSON de `request_features/` a cada
`/inference-grayscale`; o Streamlit só agrega e compara.

## Objetivo

Tratar um tema de imagens como referência de «treino» (sem rede neural),
enviar outro tema por `/inference-grayscale` com log em `request_features/`,
e no **Streamlit** montar histograma de **L** → CDF de **L** → KS, com banner
ALERTA / ATENÇÃO / TRANQUILO / INCONCLUSIVO.

A árvore é autocontida (padrão BentoML + log); o KS vive só no Streamlit.

## Entrada e saída

**Referência:** as primeiras 50 imagens de `samples/beaches/` (110 no tema)
viram `corpus_stats.json` (`just extract-features && just build-corpus-stats`).

**Lotes de demonstração (offline):** `just build-demo-batches` grava

- `batch_stats/control.json` — praias 51–100 (mesmo tema, outro trecho)
- `batch_stats/forests.json` — 50 florestas (tema divergente)

No Streamlit: amostra de imagem acima de cada histograma; construção do
histograma e da CDF de **L** em cada lado; as duas CDFs juntas; **D**,
valor-p, n efectivo.

**Leituras típicas com n = 50 imagens por lado:**

| Lote | D (aprox.) | Banner |
| :--- | ---: | :--- |
| florestas | ~0,23 | **ATENÇÃO** (D ≥ 0,10; valor-p ≈ 0,12 com n efectivo por imagens) |
| controle | ~0,05 | **TRANQUILO** |

O valor-p usa n efectivo pelas **contagens de imagens**; **D** e as curvas
de L carregam a leitura visual. Prometheus / Grafana ficam para lições
posteriores.

**Regra do banner (v1):**

- **INCONCLUSIVO** se `n_images` &lt; 8 de qualquer lado
- **ALERTA** se valor-p &lt; 0,05 **e** D ≥ 0,10
- **ATENÇÃO** se exactamente um dos dois dispara
- **TRANQUILO** se nenhum dispara

## Como executar

```bash
cd 003_ks_drift_alert_streamlit
just sync
just download-samples          # aponta para samples/ na raiz
just extract-features
just build-corpus-stats
just build-demo-batches
just streamlit                 # http://localhost:8503
```

Caminho **com servidor** (log real):

```bash
just serve                     # terminal 1
just clear-request-features
just exercise-theme forests
just snapshot-batch forests    # → batch_stats/forests.json
just clear-request-features
just exercise-theme beaches --offset=12 --count=12
just snapshot-batch control
just streamlit
```

## O que acontece por dentro

```text
imagem → convert("L") → histograma de L (pixels)
beaches[:50] → soma dos histogramas → corpus_stats.json
lote → /inference-grayscale → request_features/ → batch_stats/
Streamlit: histograma de L → CDF de L → D, valor-p → banner
```

`n_eff = n_c × n_p / (n_c + n_p)` com **n = número de imagens** (só no
valor-p; a forma da distribuição continua sendo a dos **pixels** via L).

## Comparação com a base

A base só devolve a imagem filtrada. Esta lição grava o pedido (como a linha
`020`) e analisa a distribuição de **L** no Streamlit (sem rotas
`/monitor-ks-*`).

## Testes

```bash
just test
```

[`004_prometheus_histcdf_streamlit`](../004_prometheus_histcdf_streamlit/README.md)
