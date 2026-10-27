# Lição 003 — Alerta KS de drift (BentoML + Streamlit)

## Por que estamos aqui

Este serviço pode responder **rápido** e com **HTTP 200** e, mesmo assim,
trabalhar sobre um mundo diferente do treino: outro tema de foto, outro
padrão de uso do modelo. A latência mede espera. Ela não mede se os **dados**
ainda combinam com a referência.

Nesta aula você mede essa combinação na **forma** da distribuição de
luminância **L**, resume o afastamento numa estatística **D**
(Kolmogorov–Smirnov) e produz um **alerta** quando **D** cruza um limiar.

![Fluxo L → histograma → CDF → δ → D → alerta](illustrations/01_workflow_l_to_alert.png)

## Definições (didática e formal)

### L — luminância do pixel

**Didática.** Cada pixel vira um tom de cinza: 0 = preto, 255 = branco.

**Formal.** Seja \(I\) uma imagem. Após `Image.convert("L")`,

\[
L(u,v) \in \{0,1,\ldots,255\}
\]

é a intensidade no sítio \((u,v)\). O eixo das distribuições desta aula é
**L por pixel**, não a média de L por imagem.

```python
from PIL import Image

img = Image.open("foto.jpg").convert("L")
contagens = img.histogram()  # 256 faixas
```

### Histograma

**Didática.** Conta quantos pixels caíram em cada faixa de L.

**Formal.** Com \(B\) faixas (nesta aula, tipicamente 256) e contagens
\(h_0,\ldots,h_{B-1}\),

\[
h_k = \#\{\text{pixels com } L \text{ na faixa } k\},
\qquad
N = \sum_{k=0}^{B-1} h_k.
\]

Para um **conjunto** de imagens, some os histogramas imagem a imagem.

![Histograma e CDF — exemplo mínimo](illustrations/02_hist_to_cdf_toy.png)

### CDF — função de distribuição acumulada

**Didática.** Em cada faixa: *até aqui, que fração dos pixels já passou?*
A curva sobe de 0 a 1.

**Formal.**

\[
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i
\qquad (k = 0,\ldots,B-1).
\]

**Exemplo mínimo.** Contagens \([2,1,3]\) (\(N=6\)) →
\(F = [2/6,\ 3/6,\ 6/6]\).

```text
# Variáveis:
# contagens, total, acumulado, cdf, c

total ← soma(contagens)
acumulado ← 0
cdf ← lista vazia
para cada c em contagens:
    acumulado ← acumulado + c
    acrescentar (acumulado / total) em cdf
```

### δ e D — estatística de Kolmogorov–Smirnov

**Didática.** Compare a CDF da referência \(F\) com a do lote \(G\). Em cada
faixa meça a distância vertical; **D** é a maior dessas distâncias. Se **D**
é grande, as formas de L divergem — dispare um **alerta** sobre essa
estatística.

**Formal.**

\[
\delta_k = \lvert F_k - G_k \rvert,
\qquad
D = \max_{k} \delta_k
= \sup_{x} \lvert F(x) - G(x) \rvert.
\]

![δ(L) e D = max δ](illustrations/06_delta_d.png)

### Alerta sobre D

Regra didática desta aula (centrada na estatística **D**):

- **INCONCLUSIVO** — poucas imagens de qualquer lado (&lt; 8)
- **ALERTA** — \(D \ge 0{,}10\)
- **TRANQUILO** — \(D < 0{,}10\)

[^pvalue]

[^pvalue]: O software ainda calcula um **valor-p** assintótico do KS de duas
amostras, com tamanho efetivo baseado no **número de imagens** (não no de
pixels: pixels da mesma foto não são independentes — há subtileza de graus
de liberdade / dependência espacial). Esse valor-p **não** entra na regra de
alerta do handout; trate-o como nota de rodapé estatística, não como motor
do alarme.

## Figuras do freeze (praias × florestas)

Referência = `beaches[:50]`; lote = `forests[:50]`. **D ≈ 0,23** → ALERTA
pela regra \(D \ge 0{,}10\).

| Histograma (treino) | Histograma (lote) |
| :---: | :---: |
| ![hist praias](illustrations/03_hist_beaches.png) | ![hist florestas](illustrations/04_hist_forests.png) |

![Duas CDFs com segmento em D](illustrations/05_dual_cdf.png)

Controle (`beaches[50:100]`): **D ≈ 0,05** → TRANQUILO.

## Objetivo operacional

1. Fixar um tema como referência de treino (sem rede neural).
2. Enviar outro tema (ou o mesmo) por `/inference-grayscale` com log.
3. No Streamlit, construir histograma → CDF → δ → **D** e ler o alerta sobre
   **D**.

## Entrada e saída

**Referência:** primeiras 50 de `samples/beaches/` (110 no tema) →
`corpus_stats.json`.

**Lotes offline** (`just build-demo-batches`):

- `batch_stats/control.json` — praias 51–100
- `batch_stats/forests.json` — 50 florestas

## Por que 50 imagens se há 110 por tema?

Desenho do experimento: 50 treino + 50 controle + 50 florestas, tamanhos
pareados. Não é escassez de dados.

## L por pixel vs média por imagem

| Lente | beaches[:50] vs forests[:50] | beaches[:50] vs beaches[50:100] |
| :--- | :--- | :--- |
| **L por pixel** | D ≈ 0,23 → ALERTA | D ≈ 0,05 → TRANQUILO |
| **Média de L** | D ≈ 0,54 → ALERTA | D ≈ 0,18 → ALERTA (**falso alerta** no controle) |

Por isso o handout fixa L por pixel. Ramo D:
[`docs/designs/ks-003-ramos-planejados.md`](../docs/designs/ks-003-ramos-planejados.md).

## Limiares comuns de D / KS por área

| Área | Regra típica | Fonte |
| :--- | :--- | :--- |
| Estatística (duas amostras) | \(D > c(\alpha)\sqrt{(n+m)/(nm)}\); \(c(0{,}05)\approx 1{,}358\) | [Wikipédia — KS](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test) |
| Tabelas / software | idem; \(n\) pequenos via tabela | [MetricGate](https://metricgate.com/docs/kolmogorov-smirnov-critical-values/); [Real Statistics](https://real-statistics.com/statistics-tables/two-sample-kolmogorov-smirnov-table/) |
| Astronomia | tabelas \(mnD\) | [NED / Wall](https://ned.ipac.caltech.edu/level5/Wall2/TableA_8.html) |
| FRTB P&L | verde &lt; 0,09; vermelho &gt; 0,12 | [MathWorks](https://www.mathworks.com/help/risk/profit-and-loss-attribution-workflow.html); [UE 2022/2059 art. 8](https://judict.eu/en/sla/32013R0575/32022R2059-X/article-8) |
| Credit scoring | KS como discriminação (maior = melhor) | [SAS Model Manager](https://support.sas.com/documentation/cdl/en/mdlmgrug/69919/HTML/default/n194xndt3b3y1pn1ufc0mqbsmht4.htm) |
| **Esta aula** | alerta se \(D \ge 0{,}10\) | handout |

## Ramos planejados

[`docs/designs/ks-003-ramos-planejados.md`](../docs/designs/ks-003-ramos-planejados.md):
produção mista; PSI; KS entrada×saída; pixel vs média no controle.

## Como executar

```bash
cd 003_ks_drift_alert_streamlit
just sync
just download-samples
just extract-features
just build-corpus-stats
just build-demo-batches
just generate-illustrations   # opcional: regenera illustrations/*.png
just streamlit                # http://localhost:8503
```

Com servidor:

```bash
just serve
just clear-request-features
just exercise-theme forests
just snapshot-batch forests
just streamlit
```

## O que acontece por dentro

```text
imagem → convert("L") → histograma de L (pixels)
beaches[:50] → soma → corpus_stats.json
lote → /inference-grayscale → request_features/ → batch_stats/
app: histograma → CDF → δ → D → alerta se D ≥ 0,10
```

## Comparação com a base

A base só devolve a imagem filtrada. Esta lição grava o pedido (como `020`)
e analisa a distribuição de **L** no Streamlit.

## Testes

```bash
just test
```

## Bibliografia (auditada)

1. [Kolmogorov–Smirnov (Wikipédia)](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)
2. Gama et al., *A survey on concept drift adaptation*, ACM CSUR 2014 —
   [doi:10.1145/2523813](https://doi.org/10.1145/2523813)
3. [PSI — KAscore Ongoing Monitoring](https://ketchbrookanalytics.github.io/KAscore/articles/ongoing-monitoring.html)
4. Taplin & Hunt, Risks 2019 — [MDPI](https://www.mdpi.com/2227-9091/7/2/53)
5. [Pillow — Image](https://pillow.readthedocs.io/en/stable/reference/Image.html)

Mais detalhe em prosa:
[`docs/meta-da-aula-a-formula.md`](docs/meta-da-aula-a-formula.md).

[`004_prometheus_histcdf_streamlit`](../004_prometheus_histcdf_streamlit/README.md)
