# Booklet — do serviço em produção ao alerta KS

**Lição:** `003_ks_drift_alert_streamlit`  
**Companheiro prático:** [`../README.md`](../README.md) · app Streamlit: [`../app.py`](../app.py)

---

## Sumário

1. [Por que este booklet existe](#1-por-que-este-booklet-existe)
2. [DevOps: o serviço que responde](#2-devops-o-serviço-que-responde)
3. [MLOps: servir o modelo e observar o mundo](#3-mlops-servir-o-modelo-e-observar-o-mundo)
4. [Saúde HTTP versus adequação dos dados](#4-saúde-http-versus-adequação-dos-dados)
5. [BentoML: colocar a API no ar](#5-bentoml-colocar-a-api-no-ar)
6. [Registro de pedidos](#6-registro-de-pedidos)
7. [Imagens, pixels e luminância L](#7-imagens-pixels-e-luminância-l)
8. [Histograma](#8-histograma)
9. [Função de distribuição acumulada (CDF)](#9-função-de-distribuição-acumulada-cdf)
10. [Exemplo numérico mínimo](#10-exemplo-numérico-mínimo)
11. [Kolmogorov–Smirnov: de δ a D](#11-kolmogorovsmirnov-de-δ-a-d)
12. [Alerta sobre D](#12-alerta-sobre-d)
13. [Janela temporal no monitoramento](#13-janela-temporal-no-monitoramento)
14. [O experimento desta aula](#14-o-experimento-desta-aula)
15. [Mapa do código e como executar](#15-mapa-do-código-e-como-executar)
16. [Glossário curto](#16-glossário-curto)
17. [Bibliografia](#17-bibliografia)

---

## 1. Por que este booklet existe

Imagine um serviço de imagens em produção: o cliente envia uma foto, a API
devolve a versão em cinza, o status é **200**, o tempo de resposta está baixo.
Do ponto de vista de disponibilidade, o dia está tranquilo.

Agora mude o *conteúdo* das fotos — de praias para florestas, de estúdio para
rua à noite — e mantenha o mesmo endpoint. O HTTP continua verde. A latência
continua aceitável. O que mudou foi o **mundo** que chega ao modelo.

Este booklet acompanha o caminho completo até a pergunta operacional:

> as luminâncias dos pixels que estão chegando ainda se parecem com as do
> treino?

A resposta, nesta aula, passa por histograma, CDF, distância vertical δ e a
estatística de Kolmogorov–Smirnov **D**. Quando **D** cruza um limiar, o
painel mostra **ALERTA**.

O fluxo visual está em
[`../illustrations/01_workflow_l_to_alert.png`](../illustrations/01_workflow_l_to_alert.png).

---

## 2. DevOps: o serviço que responde

**Razão de ser.** DevOps, neste contexto de aula, é a disciplina de
*colocar um processo no ar e mantê-lo utilizável*: empacotar, servir,
receber pedidos, devolver respostas e saber se a máquina ainda está viva.

Um serviço HTTP típico responde a perguntas como:

| Pergunta | O que se mede |
| :--- | :--- |
| O processo está no ar? | processo, porta, health check |
| O cliente recebe resposta? | código HTTP (200, 4xx, 5xx) |
| A espera é aceitável? | latência (p50, p95, …) |
| Há erros? | taxa de falha, logs de exceção |

Essas métricas descrevem a **saúde da tubulação**: o servidor aceita
conexões, o código não explode, a rede entrega bytes. Elas são
indispensáveis — e insuficientes sozinhas quando o produto é um modelo de
aprendizado de máquina.

Nesta pasta da lição, o serviço BentoML expõe rotas de inferência
(`/inference-grayscale`, entre outras). O handout prático descreve como
subir e exercitar esse serviço em [`../README.md`](../README.md).

---

## 3. MLOps: servir o modelo e observar o mundo

**Razão de ser.** MLOps estende o ciclo de servir: além de “a API responde?”,
aparece “os dados e o comportamento do modelo ainda fazem sentido?”.

Num fluxo enxuto de *serving* com observação:

```text
# Variáveis:
# imagem — arquivo enviado pelo cliente
# resposta — saída do modelo / filtro
# features — resumo estatístico gravado no log
# referência — distribuição de treino (corpus)
# lote — agregação de pedidos recentes
# D — estatística KS entre referência e lote

imagem chega no endpoint
resposta ← modelo(imagem)
features ← extrair luminância / histograma da imagem
gravar features no log de pedidos
periodicamente:
    lote ← agregar pedidos da janela temporal
    D ← KS(referência, lote)
    se D ≥ limiar → ALERTA
```

Três ideias que este booklet amarra:

1. **Servir** — BentoML (ou equivalente) expõe o modelo como API.
2. **Registrar** — cada pedido relevante deixa um vestígio mensurável
   (aqui: features de imagem em JSON).
3. **Comparar** — um painel (Streamlit) confronta o corpus de treino com o
   lote atual e resume o afastamento em **D**.

O “drift” de que falamos é mudança na **forma da distribuição de entrada**
(luminância **L**), medida entre um conjunto de referência e um lote de
produção.

---

## 4. Saúde HTTP versus adequação dos dados

**Razão de ser.** Separar duas camadas evita o falso conforto do “tudo
verde”.

### Camada A — saúde do serviço

- Porta aberta, processo vivo.
- Respostas 200 (ou códigos esperados).
- Latência dentro do orçamento.
- Sem exceções em cascata.

### Camada B — adequação dos dados

- As imagens de produção ainda se parecem, em distribuição, com o treino?
- A estatística **D** (forma de **L**) está abaixo do limiar de alerta?
- Há imagens suficientes no lote para a comparação ser legível?

Um serviço pode estar **A-saudável** e **B-desalinhado** ao mesmo tempo:
HTTP 200 rápido sobre fotos de um domínio que o treino quase não viu.

Nesta aula, a latência mede **espera**. A estatística **D** mede
**afastamento de forma** entre a CDF de luminância da referência e a do
lote. O alerta do handout responde a **D**.

---

## 5. BentoML: colocar a API no ar

**Razão de ser.** BentoML empacota o código de inferência e sobe um servidor
HTTP com rotas tipadas — o aluno exercita o mesmo padrão que aparece em
deployments reais enxutos.

Nesta lição, a classe de serviço (arquivo `service.py` na pasta da aula)
registra, entre outras, a rota `/inference-grayscale`. Em linhas gerais:

1. O cliente envia uma imagem.
2. O serviço **registra** features da imagem (log de pedido).
3. O serviço aplica a conversão a cinza e devolve a imagem processada.

Comandos típicos (detalhe e ordem completa no
[`../README.md`](../README.md)):

```bash
cd 003_ks_drift_alert_streamlit
just sync
just serve
# terminal dedicado: API na porta 3333
```

Enquanto o servidor está no ar, outro terminal pode enviar um tema de
amostras (`just exercise-theme …`) e depois agregar o log
(`just snapshot-batch …`). O Streamlit (`just streamlit`, porta 8503)
lê o corpus de referência e o lote agregado.

O que importa para este booklet: **servir** e **observar** andam juntos.
A resposta HTTP é o produto imediato; o log é a matéria-prima do
monitoramento de dados.

---

## 6. Registro de pedidos

**Razão de ser.** Sem vestígio do que chegou, só resta a saúde HTTP. Com
log de features, dá para reconstruir a distribuição de produção.

Nesta aula, cada chamada a `/inference-grayscale` grava um JSON em
`request_features/` (timestamp + id, histogramas de canais, metadados).
Depois, um *snapshot* agrega esses arquivos em `batch_stats/<nome>.json`.

Fluxo resumido:

```text
POST /inference-grayscale
  → log JSON em request_features/
  → resposta = imagem em cinza

snapshot-batch
  → soma histogramas do log
  → batch_stats/<lote>.json
  → limpa (ou prepara) a pasta de log para o próximo exercício
```

O painel Streamlit em [`../app.py`](../app.py) compara
`corpus_stats.json` (referência de treino) com o JSON do lote escolhido
na barra lateral.

Há também um caminho **offline**: `just build-demo-batches` materializa
lotes de demonstração sem precisar do servidor no ar. Serve para estudar
histograma → CDF → **D** com números estáveis.

---

## 7. Imagens, pixels e luminância L

**Razão de ser.** Precisamos de um eixo numérico comum entre fotos
diferentes. Nesta aula, esse eixo é a luminância por pixel.

### Formal

Seja \(I\) uma imagem. Após a conversão Pillow `Image.convert("L")`,

\[
L(u,v) \in \{0,1,\ldots,255\}
\]

é a intensidade no sítio \((u,v)\): **0** = preto, **255** = branco.

### Por que L por pixel (e não a média por imagem)

O handout fixa a distribuição de **L por pixel** porque ela descreve a
*textura tonal* do conjunto: céu claro, sombra densa, folhagem média,
etc. A **média de L por imagem** comprime cada foto a um único número;
no controle de mesmo tema (outro trecho de praias), essa compressão
infla **D** e gera **falso alerta**, enquanto L por pixel permanece
tranquilo.

| Lente | praias[:50] vs florestas[:50] | praias[:50] vs praias[50:100] |
| :--- | :--- | :--- |
| **L por pixel** | \(D \approx 0{,}23\) → ALERTA | \(D \approx 0{,}05\) → TRANQUILO |
| **Média de L** | \(D \approx 0{,}54\) → ALERTA | \(D \approx 0{,}18\) → ALERTA (falso no controle) |

Trecho típico:

```python
from PIL import Image

img = Image.open("foto.jpg").convert("L")
contagens = img.histogram()  # 256 faixas
```

---

## 8. Histograma

**Didática.** Conta quantos pixels caíram em cada faixa de luminância.

**Formal.** Com \(B\) faixas (nesta aula, tipicamente \(B = 256\)) e
contagens \(h_0,\ldots,h_{B-1}\),

\[
h_k = \#\{\text{pixels com } L \text{ na faixa } k\},
\qquad
N = \sum_{k=0}^{B-1} h_k.
\]

Para um **conjunto** de imagens (corpus ou lote), some os histogramas
imagem a imagem: o \(h_k\) agregado é a soma dos \(h_k\) individuais, e
\(N\) passa a ser o total de pixels do conjunto.

O Streamlit permite reagrupar faixas (16 a 256) para visualizar a mesma
comparação em resoluções diferentes; a definição de **D** permanece a
mesma na grade escolhida.

Figura didática:
[`../illustrations/02_hist_to_cdf_toy.png`](../illustrations/02_hist_to_cdf_toy.png).

---

## 9. Função de distribuição acumulada (CDF)

**Didática.** Em cada faixa: *até aqui, que fração dos pixels já
passou?* A curva sobe de 0 a 1.

**Formal.** A CDF empírica discreta na grade do histograma é

\[
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i
\qquad (k = 0,\ldots,B-1).
\]

Propriedades úteis:

- \(F_{-1}\) conceitualmente 0; \(F_{B-1} = 1\) (se \(N > 0\)).
- \(F\) é não decrescente.
- Dois conjuntos com o mesmo \(N\) e as mesmas contagens têm a mesma
  \(F\); o que interessa na comparação é a **forma** de \(F\) versus
  \(G\) (CDF do lote).

Pseudocódigo (mais de cinco linhas → variáveis declaradas):

```text
# Variáveis:
# contagens — histograma de L (lista de inteiros ≥ 0)
# total — soma(contagens) = número de pixels
# acumulado — soma parcial até a faixa atual
# cdf — lista de frações em [0, 1]
# c — contagem da faixa corrente

total ← soma(contagens)
acumulado ← 0
cdf ← lista vazia
para cada c em contagens:
    acumulado ← acumulado + c
    acrescentar (acumulado / total) em cdf
```

No código da lição, isso corresponde a `cumulative_distribution` em
`histogram.py`, usado por `ks_compare.py` e pelo app.

---

## 10. Exemplo numérico mínimo

Considere um histograma de brinquedo com **três** faixas e contagens

\[
\mathbf{h} = [2,\ 1,\ 3].
\]

Então \(N = 2+1+3 = 6\) e

\[
\begin{align*}
F_0 &= \frac{2}{6} = \frac{1}{3}, \\
F_1 &= \frac{2+1}{6} = \frac{3}{6} = \frac{1}{2}, \\
F_2 &= \frac{2+1+3}{6} = \frac{6}{6} = 1.
\end{align*}
\]

Em lista: CDF = `[2/6, 3/6, 6/6]`.

Agora compare com um segundo histograma \(\mathbf{g} = [1,\ 1,\ 4]\)
(\(N'=6\)):

\[
G = \Bigl[\tfrac{1}{6},\ \tfrac{2}{6},\ 1\Bigr].
\]

As distâncias verticais:

\[
\begin{align*}
\delta_0 &= \lvert F_0 - G_0 \rvert = \lvert 2/6 - 1/6 \rvert = 1/6, \\
\delta_1 &= \lvert 3/6 - 2/6 \rvert = 1/6, \\
\delta_2 &= \lvert 1 - 1 \rvert = 0.
\end{align*}
\]

Logo

\[
D = \max_k \delta_k = \frac{1}{6} \approx 0{,}1667.
\]

Com a regra didática \(D \ge 0{,}10\), este brinquedo já cairia em
**ALERTA** (supondo amostras grandes o bastante para sair de
INCONCLUSIVO — ver capítulo do alerta).

---

## 11. Kolmogorov–Smirnov: de δ a D

**Razão de ser.** Queremos um único número que resuma “quão longe estão
as duas formas de luminância”.

Sejam \(F\) a CDF da referência (treino) e \(G\) a CDF do lote
(produção), ambas na mesma grade de faixas. Defina

\[
\delta_k = \lvert F_k - G_k \rvert,
\qquad
D = \max_{k} \delta_k
= \sup_{x} \lvert F(x) - G(x) \rvert.
\]

Interpretação geométrica: sobreponha as duas curvas CDF; em cada abscissa
de L meça a distância vertical; **D** é o maior desses segmentos.

Figura:
[`../illustrations/06_delta_d.png`](../illustrations/06_delta_d.png).

Pseudocódigo:

```text
# Variáveis:
# F_ref, F_lote — CDFs na mesma grade de L
# delta — lista de |F_ref − F_lote|
# D — máximo de delta
# i_star — índice onde o máximo ocorre

delta ← lista vazia
para i de 0 até comprimento(F_ref) − 1:
    acrescentar |F_ref[i] − F_lote[i]| em delta
D ← máximo(delta)
i_star ← argmáximo(delta)
```

No repositório, `ks_statistic` em `ks_compare.py` implementa exatamente
\(D = \max |F_a - F_b|\).

### Nota de rodapé: valor-p

O software ainda calcula um **valor-p** assintótico clássico do teste KS
de duas amostras, com tamanho efetivo baseado no **número de imagens**
de cada lado (pixels da mesma foto **não** são independentes — há
subtileza de graus de liberdade e dependência espacial). Esse valor-p
**não** entra na regra de alerta do handout: trate-o como nota
estatística no rodapé do painel, não como motor do alarme. O alerta
desta aula responde a **D**.

---

## 12. Alerta sobre D

**Razão de ser.** Transformar a estatística contínua **D** numa decisão
operacional legível no painel.

Regra didática desta aula (`banner.py` / `alert_on_d`):

| Estado | Condição |
| :--- | :--- |
| **INCONCLUSIVO** | menos de 8 imagens na referência **ou** no lote |
| **ALERTA** | \(D \ge 0{,}10\) |
| **TRANQUILO** | \(D < 0{,}10\) (com amostras suficientes) |

O limiar \(0{,}10\) é uma escolha **de handout**: simples de memorizar e
alinhada à ordem de grandeza do experimento praias × florestas
(\(D \approx 0{,}23\)) versus o controle de mesmo tema
(\(D \approx 0{,}05\)). Em produção real, o limiar seria calibrado ao
risco do negócio e à variabilidade histórica.

Outras áreas usam regras diferentes (valores críticos tabulares,
faixas regulatórias, KS como índice de discriminação). O
[`../README.md`](../README.md) traz uma tabela de referência; o que
importa na prática da aula é: **o alarme dispara sobre D**.

---

## 13. Janela temporal no monitoramento

**Razão de ser.** Em produção, “o lote” quase nunca é “todas as imagens
desde o início dos tempos”. Monitoramento de dados trabalha com
**janelas**.

### Ideia

Fixe:

- **Referência** — corpus de treino (ou um baseline estável revisado
  periodicamente).
- **Janela de produção** — por exemplo, os pedidos dos **últimos 30
  dias** (ou 7 dias, ou a última semana calendário — o número é uma
  política).

Compare a CDF agregada da referência com a CDF agregada **somente** dos
pedidos dentro da janela. O **D** passa a responder:

> nos últimos 30 dias, a forma de L ainda combina com o treino?

### Por que limitar no tempo

| Aspecto | Efeito da janela |
| :--- | :--- |
| Relevância | o alerta reflete o presente operacional |
| Volume | evita diluir um desvio recente numa história antiga enorme |
| Operação | times sabem o período sob escrutínio |
| Reprocessamento | snapshots podem ser refeitos por calendário |

### Como isso aparece na aula

No exercício didático, a “janela” é o lote que você monta de propósito
(`forests`, `control`, etc.): um conjunto fechado e nomeado. Em um
sistema real com timestamps no log (`logged_at` nos JSON de
`request_features/`), a agregação filtraria

\[
\{\text{pedidos com } t_{\text{agora}} - 30\text{ dias} \le t_{\text{log}} \le t_{\text{agora}}\}.
\]

O cálculo matemático (histograma → CDF → δ → **D**) é o mesmo; muda só
**quais** imagens entram no histograma do lado produção.

### Política mínima sugerida (estudo)

1. Escolher a duração da janela (ex.: 30 dias).
2. Agregar histogramas só dessa fatia.
3. Exigir um mínimo de imagens (nesta aula: 8) antes de sair de
   INCONCLUSIVO.
4. Alertar se \(D \ge\) limiar.
5. Revisar a referência quando o negócio mudar de domínio de propósito
   (novo produto visual, nova câmera, novo mercado).

---

## 14. O experimento desta aula

**Desenho.** Tema de referência = primeiras 50 praias
(`samples/beaches/`). Lotes offline típicos:

- `batch_stats/control.json` — praias 51–100 (mesmo tema, outro trecho).
- `batch_stats/forests.json` — 50 florestas.

Resultados de referência do freeze de figuras:

| Comparação | \(D\) típico | Alerta (\(D \ge 0{,}10\)) |
| :--- | :--- | :--- |
| praias[:50] vs florestas[:50] | \(\approx 0{,}23\) | ALERTA |
| praias[:50] vs praias[50:100] | \(\approx 0{,}05\) | TRANQUILO |

Figuras:

| Histograma (treino) | Histograma (lote) |
| :---: | :---: |
| ![hist praias](../illustrations/03_hist_beaches.png) | ![hist florestas](../illustrations/04_hist_forests.png) |

CDF sobreposta:
[`../illustrations/05_dual_cdf.png`](../illustrations/05_dual_cdf.png).

Por que 50 imagens se há 110 por tema? Desenho do experimento: 50
treino + 50 controle + 50 florestas, tamanhos pareados — clareza
didática, não escassez de dados.

---

## 15. Mapa do código e como executar

### Peças principais (pasta da lição)

| Artefato | Papel |
| :--- | :--- |
| `service.py` | API BentoML; log em `/inference-grayscale` |
| `request_log.py` | grava JSON em `request_features/` |
| `histogram.py` | histograma e CDF |
| `ks_compare.py` | \(D\) (e valor-p assintótico, nota de rodapé) |
| `banner.py` | regra INCONCLUSIVO / ALERTA / TRANQUILO sobre **D** |
| [`../app.py`](../app.py) | painel Streamlit |
| `corpus_stats.json` | referência agregada de treino |
| `batch_stats/*.json` | lotes agregados |
| `illustrations/` | figuras do handout e do app |

### Caminho offline (estudo de D sem servidor)

```bash
cd 003_ks_drift_alert_streamlit
just sync
just download-samples
just extract-features
just build-corpus-stats
just build-demo-batches
just streamlit
# http://localhost:8503
```

### Caminho com servidor (log real)

Ver sequência completa em [`../README.md`](../README.md): `just serve`,
`just exercise-theme`, `just snapshot-batch`, depois `just streamlit`.

### O que acontece por dentro

```text
imagem → convert("L") → histograma de L (pixels)
beaches[:50] → soma → corpus_stats.json
lote → /inference-grayscale → request_features/ → batch_stats/
app: histograma → CDF → δ → D → alerta se D ≥ 0,10
```

Testes: `just test`.

---

## 16. Glossário curto

| Termo | Significado nesta aula |
| :--- | :--- |
| **L** | luminância do pixel após `convert("L")`, em \(\{0,\ldots,255\}\) |
| **Histograma** | contagens \(h_k\) por faixa de L |
| **CDF** | \(F_k = (1/N)\sum_{i\le k} h_i\) |
| **δ** | \(\lvert F_k - G_k \rvert\) |
| **D** | \(\max_k \delta_k\) (Kolmogorov–Smirnov) |
| **Referência / corpus** | distribuição de treino agregada |
| **Lote / produção** | agregação de pedidos (ou batch demo) |
| **ALERTA** | \(D \ge 0{,}10\) com amostras suficientes |
| **Janela temporal** | fatia de pedidos (ex.: últimos 30 dias) usada no lote |

Resumo condensado também em
[`meta-da-aula-a-formula.md`](meta-da-aula-a-formula.md).

---

## 17. Bibliografia

1. [Kolmogorov–Smirnov (Wikipédia)](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)
2. Gama et al., *A survey on concept drift adaptation*, ACM CSUR 2014 —
   [doi:10.1145/2523813](https://doi.org/10.1145/2523813)
3. [Pillow — Image](https://pillow.readthedocs.io/en/stable/reference/Image.html)
4. Handout da lição: [`../README.md`](../README.md)

---

*Fim do booklet. Para o passo a passo de execução e as figuras do
experimento, use o README da pasta da lição.*
