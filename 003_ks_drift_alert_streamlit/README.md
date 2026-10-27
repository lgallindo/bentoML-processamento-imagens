# Lição 003 — Alerta KS de drift (BentoML + Streamlit)

## Por que estamos aqui

O servidor pode estar “saudável” (responde 200, latência ok) e mesmo assim
estar **recebendo um mundo diferente** daquele em que o fluxo foi pensado:
outro tema de foto, outro jeito de usar o modelo, um lote que já não combina
com a referência de treino. Essa inadequação não grita no `/metrics` de
latência. Ela aparece na **forma dos dados**.

Nesta aula medimos essa forma com uma variável só — a luminância **L** de
cada pixel — e transformamos o afastamento entre duas curvas numa estatística
**D** (Kolmogorov–Smirnov). Com limiares em **D** e no valor-p, montamos um
**alerta**: o mesmo tipo de sinal que, num sistema real, poderia acionar
página, ticket ou rule de monitoramento. Em uma frase: **monitoramos se o
servidor ainda é adequado aos dados que chegam (ou a um uso distinto do
modelo) alertando sobre a variável KS.**

Como chegamos lá, passo a passo no Streamlit: histograma de L → CDF de L →
diferença absoluta δ entre as CDFs → **D = max δ** → banner.

## Variável: **L** (luminância de cada pixel)

**Não** usamos a luminância média da imagem como eixo X. O eixo das
distribuições é **L de cada pixel**: cinza 0…255 depois de
`Image.convert("L")`. Histograma, CDF e KS agregam **pixels** de todas as
imagens do conjunto.

| Símbolo | O que é |
| :--- | :--- |
| **L** | Valor de cinza do **pixel** (0 = preto … 255 = branco) |
| Unidade da amostra | **Pixel** (não a média por imagem; RGB por canal fica de fora deste KS) |
| Comparação | distribuição de L na **referência** vs distribuição de L no **lote** |

### Como extrair L de uma imagem (prova de conceito)

```python
from PIL import Image

img = Image.open("foto.jpg").convert("L")  # cada pixel → L ∈ {0, …, 255}
contagens = img.histogram()               # 256 faixas: quantos pixels têm cada L
# Some `contagens` de várias imagens → histograma do conjunto → CDF → KS.
```

No serviço da lição, o mesmo L entra no JSON de `request_features/` a cada
`/inference-grayscale`; o Streamlit agrega e compara.

## Objetivo operacional

1. Fixar um tema como referência de «treino» (sem rede neural).
2. Enviar outro tema (ou o mesmo) por `/inference-grayscale` com log.
3. No Streamlit, ver se **D** e o valor-p disparam o banner — ensaio de
   alerta sobre adequação dados↔serviço.

Banner: ALERTA / SINAL PARCIAL / TRANQUILO / INCONCLUSIVO.

## Entrada e saída

**Referência:** as primeiras 50 imagens de `samples/beaches/` (110 no tema)
viram `corpus_stats.json`.

**Lotes de demonstração (offline):** `just build-demo-batches` grava

- `batch_stats/control.json` — praias 51–100 (mesmo tema, outro trecho)
- `batch_stats/forests.json` — 50 florestas (tema divergente)

No Streamlit: amostra acima de cada histograma; CDF; δ; **D** e valor-p.

**Leituras típicas (50 imagens por lado):**

| Lote | D (aprox.) | Banner |
| :--- | ---: | :--- |
| florestas | ~0,23 | **SINAL PARCIAL** (D ≥ 0,10; valor-p ainda alto com amostra por imagens) |
| controle | ~0,05 | **TRANQUILO** |

**Regra do banner (v1):**

- **INCONCLUSIVO** se poucas imagens de qualquer lado
- **ALERTA** se valor-p &lt; 0,05 **e** D ≥ 0,10
- **SINAL PARCIAL** se exatamente um dos dois dispara
- **TRANQUILO** se nenhum dispara

### Do histograma à CDF (rascunho)

```text
# Variáveis:
# contagens — lista de inteiros do histograma de L
# total — soma(contagens) = número de pixels no conjunto
# acumulado — soma parcial ao percorrer as faixas
# cdf — lista de F(L) em [0, 1]
# c — contagem da faixa corrente

total ← soma(contagens)
acumulado ← 0
cdf ← lista vazia
para cada c em contagens:
    acumulado ← acumulado + c
    acrescentar (acumulado / total) em cdf
```

### Das duas CDFs a δ e a D

```text
# Variáveis:
# F_ref, F_lote — CDFs de L na mesma grade
# delta — δ(i) = |F_ref[i] − F_lote[i]|
# D — máximo de delta (estatística KS)
# i_star — faixa do máximo

delta ← lista vazia
para i de 0 até comprimento(F_ref) − 1:
    acrescentar |F_ref[i] − F_lote[i]| em delta
D ← máximo(delta)
i_star ← argmáximo(delta)
```

## Ramos planejados (rascunho)

Detalhe em
[`docs/designs/ks-003-ramos-planejados.md`](../docs/designs/ks-003-ramos-planejados.md).

1. **Produção mista praias + paisagem** — mesmo KS, mas o lote junta
   `beaches/` e `forests/` num único batch (tráfego misturado).
2. **Segundo ramo** — a definir; aguardando a próxima instrução.

## Como executar

```bash
cd 003_ks_drift_alert_streamlit
just sync
just download-samples
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
just snapshot-batch forests
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
Streamlit: histograma → CDF → δ=|F_ref−F_lote| → D=max δ → banner (alerta)
```

## Comparação com a base

A base só devolve a imagem filtrada. Esta lição grava o pedido (como a linha
`020`) e analisa a distribuição de **L** no Streamlit.

## Testes

```bash
just test
```

[`004_prometheus_histcdf_streamlit`](../004_prometheus_histcdf_streamlit/README.md)
