# Aula 008 — Alerta PSI de drift (BentoML + Streamlit)

## Por que estamos aqui

Este serviço pode responder **rápido** e com **HTTP 200** e, mesmo assim,
trabalhar sobre um mundo diferente do treino: outro tema de foto, outro
padrão de uso do modelo. A latência mede espera. Ela não mede se os **dados**
ainda combinam com a referência.

Nesta aula você resume o afastamento entre a distribuição de referência e a
do lote atual no **Population Stability Index (PSI)** e produz um **alerta**
quando o índice cruza faixas clássicas de monitoramento de scorecards.

## Luminância L

Uma fotografia digital é uma grade de pontos — os **pixels**. Em cores, cada
pixel costuma carregar três canais (vermelho, verde, azul). Para falar de
“quão claro ou escuro” é o ponto, convertemos a imagem para tons de cinza:
preto num extremo, branco no outro, e uma escada de cinzas no meio.

Na prática isso é `Image.convert("L")` no Pillow. Cada pixel passa a um
inteiro de **0** (preto) a **255** (branco). Chamamos esse valor de
**luminância** e o denotamos por **L**.

```python
from PIL import Image

img = Image.open("foto.jpg").convert("L")
media_L = sum(img.getdata()) / (img.width * img.height)
```

## Duas variáveis monitoradas

| Caminho | Variável | Unidade | Papel nesta aula |
| :--- | :--- | :--- | :--- |
| **P2** | média de L por imagem | uma observação por foto | **alerta principal** |
| **P1** | histograma de L por pixel | pixel | espelho da aula KS |

Em **P2**, as faixas vêm dos **quantis da referência** (padrão: 10 faixas).
Cada imagem da referência e do lote cai numa faixa; as massas relativas
alimentam o PSI.

Em **P1**, usamos o histograma agregado de L nos pixels (mesmo espírito da
aula KS) e convertemos contagens em massas. O número P1 existe para você
comparar sensibilidade com o \(D\) de Kolmogorov–Smirnov; o semáforo
operacional desta pasta é o **P2**.

## Fórmula do PSI

Com as mesmas \(K\) faixas na referência e no lote,

\[
\mathrm{PSI}
= \sum_{b}
\bigl(p_{\mathrm{lote}}[b] - p_{\mathrm{ref}}[b]\bigr)
\cdot
\ln\frac{p_{\mathrm{lote}}[b]}{p_{\mathrm{ref}}[b]}.
\]

Quando alguma massa é zero, suavizamos com \(\varepsilon\) (padrão
\(10^{-6}\)):

```text
# Variáveis:
# p_ref[b], p_lote[b] — massas relativas na faixa b (soma = 1)
# eps — suavização se massa zero (ex.: 1e-6)
# PSI, b, pr, pl

PSI ← 0
para cada b:
    pr ← max(p_ref[b], eps)
    pl ← max(p_lote[b], eps)
    PSI ← PSI + (pl − pr) · ln(pl / pr)
```

## Faixas de alerta (crédito / scorecards)

Cortes clássicos de monitoramento contínuo de scorecards (Siddiqi e
materiais de *ongoing monitoring*):

| Estado | Condição | O que significa | Ação típica |
| :--- | :--- | :--- | :--- |
| **INCONCLUSIVO** | \(n_{\mathrm{ref}} &lt; 8\) **ou** \(n_{\mathrm{lote}} &lt; 8\) | Ainda há poucas imagens | Esperar mais pedidos na janela |
| **ESTÁVEL** | ambos \(n \ge 8\) e PSI &lt; 0,10 | Lote compatível com a referência | Seguir monitorando |
| **INVESTIGAR** | ambos \(n \ge 8\) e 0,10 ≤ PSI ≤ 0,25 | Mudança moderada | Abrir ticket / olhar tema |
| **MUDANÇA FORTE** | ambos \(n \ge 8\) e PSI &gt; 0,25 | Afastamento forte | Investigar com prioridade |

No código interno os estados EN são `QUIET` / `WATCH` / `ALERT` /
`INCONCLUSIVE`; a UI e este handout usam os rótulos em português acima.

## Números do freeze (praias × florestas)

Referência = primeiras **50** praias (`samples/beaches/`).
P2 usa **10 faixas por quantis** da referência; P1 usa histograma de L
com 256 faixas (pixels).

| Lote | Conteúdo | PSI P2 (média L) | Leitura P2 | PSI P1 (pixel L) | Leitura P1 | KS-D (ref.) |
| :--- | :--- | ---: | :--- | ---: | :--- | ---: |
| `control` | praias 51–100 | **0,259** | MUDANÇA FORTE (limiar) | **0,060** | ESTÁVEL | ≈ 0,051 |
| `forests` | 50 florestas | **4,300** | MUDANÇA FORTE | **0,301** | MUDANÇA FORTE | ≈ 0,231 |

Calibração: com \(n=50\) e 10 quantis, cada faixa da referência tem cerca
de cinco imagens. O segundo bloco de praias desloca um pouco as médias de
L e o **P2** do controle fica **logo acima** do corte clássico 0,25
(0,259). As florestas disparam para ~4,3 — uma ordem de magnitude acima.
O espelho **P1** (pixels) separa limpo com as mesmas faixas de crédito:
controle estável (0,060), florestas mudança forte (0,301).

Mantemos os cortes 0,10 / 0,25 do crédito: não estão “claramente
errados” para imagens (florestas e P1 batem com a leitura esperada); o
que o freeze ensina é que **P2 é mais sensível** em amostras curtas, e o
número medido no controle deve entrar no handout em vez de forçar um
corte ad hoc.

## Objetivo operacional

1. Fixar um tema como referência de treino (sem rede neural).
2. Materializar lotes offline (ou enviar por `/inference-grayscale` com log).
3. No Streamlit, ler **PSI P2** (média de L), as faixas de alerta, e o
   espelho **P1** (pixels).

## Entrada e saída

**Referência:** primeiras 50 de `samples/beaches/` → `corpus_stats.json`
(inclui `luminance_means` e histogramas de pixel).

**Lotes offline** (`just build-demo-batches`):

- `batch_stats/control.json` — praias 51–100
- `batch_stats/forests.json` — 50 florestas

## Estrutura da pasta (arquivos principais)

```text
008_psi_drift_alert_streamlit/
  README.md                 # este handout
  app.py                    # Streamlit: PSI P2/P1 + faixas
  service.py                # BentoML /inference-grayscale + log
  alert_psi.py              # ESTÁVEL / INVESTIGAR / MUDANÇA FORTE
  psi.py                    # PSI, massas, quantis (P2) e pixels (P1)
  ks_compare.py             # D opcional (comparação lado a lado)
  histogram.py              # L, histograma, CDF
  corpus_stats.py           # features/ → estatística de treino
  request_stats.py          # request_features/ → lote (+ luminance_means)
  plotting.py               # histogramas, massas, médias
  corpus_stats.json         # freeze: praias[:50]
  batch_stats/              # control.json, forests.json, …
  request_features/         # log vivo (gitkeep; JSON ignorados)
  features/                 # saídas de extract
  scripts/
    extract_image_features.py
    build_corpus_stats.py
    build_batch_from_theme.py
    exercise_theme.py
    snapshot_batch.py
    verify_psi.py
  tests/
  justfile
```

## Como executar

Caminho **offline** (lotes já materializados em JSON, sem servidor):

```bash
cd 008_psi_drift_alert_streamlit
# entra na pasta da aula

just sync
# cria/atualiza .venv e instala dependências do pyproject (uv)

just download-samples
# aponta para samples/{beaches,forests,balls}/ na raiz do repositório

just extract-features
# extrai histograma L e média de L das primeiras 50 praias → features/*.json

just build-corpus-stats
# agrega features/ → corpus_stats.json (com luminance_means)

just build-demo-batches
# grava batch_stats/control.json e batch_stats/forests.json

just verify-psi control
just verify-psi forests
# imprime PSI P2/P1 e a leitura das faixas

just streamlit
# sobe o app em http://localhost:8508
```

Caminho **com servidor** (log real em `request_features/`):

```bash
just serve
# terminal 1: BentoML com /inference-grayscale na porta 3338

just clear-request-features
just exercise-theme forests
just snapshot-batch forests

just streamlit
# compara corpus_stats.json com o lote escolhido na barra lateral
```

## O que acontece por dentro

```text
imagem → convert("L") → média de L (P2) + histograma de pixels (P1)
beaches[:50] → soma → corpus_stats.json (luminance_means + histograms)
lote → batch_stats/ (offline) ou /inference-grayscale → request_features/
app: massas → PSI → faixas ESTÁVEL / INVESTIGAR / MUDANÇA FORTE
```

## Testes

```bash
just test
```

## Bibliografia (auditada)

1. [PSI — KAscore Ongoing Monitoring](https://ketchbrookanalytics.github.io/KAscore/articles/ongoing-monitoring.html)
2. Siddiqi, *Credit Risk Scorecards* (faixas clássicas 0,10 / 0,25)
3. Taplin & Hunt, Risks 2019 — [MDPI](https://www.mdpi.com/2227-9091/7/2/53)
4. [Pillow — Image](https://pillow.readthedocs.io/en/stable/reference/Image.html)
5. Kolmogorov–Smirnov (comparação opcional com \(D\)) —
   [Wikipédia](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)

## Valores medidos (freeze local)

Confirmados com `just verify-psi control` e `just verify-psi forests`
após `just build-demo-batches`:

| Lote | PSI P2 | Faixa P2 | PSI P1 | Faixa P1 | KS-D |
| :--- | ---: | :--- | ---: | :--- | ---: |
| control | 0,259 | MUDANÇA FORTE (limiar) | 0,060 | ESTÁVEL | 0,051 |
| forests | 4,300 | MUDANÇA FORTE | 0,301 | MUDANÇA FORTE | 0,231 |
