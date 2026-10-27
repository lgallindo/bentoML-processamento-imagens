# Lição 003 — Alerta KS de drift (BentoML + Streamlit)

Do serviço em produção ao alerta sobre **D**. O painel vivo está em
[`app.py`](app.py).

## Sumário

1. [Por que estamos aqui](#1-por-que-estamos-aqui)
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
14. [Limiares de D / KS em outros contextos](#14-limiares-de-d--ks-em-outros-contextos)
15. [O experimento desta aula](#15-o-experimento-desta-aula)
16. [Estrutura da pasta](#16-estrutura-da-pasta)
17. [Como executar](#17-como-executar)
18. [Glossário](#18-glossário)
19. [Testes](#19-testes)
20. [Bibliografia](#20-bibliografia)

---

## 1. Por que estamos aqui

Imagine um serviço de imagens em produção: o cliente envia uma foto, a API
devolve a versão em cinza, o status é **200**, o tempo de resposta está baixo.
Do ponto de vista de disponibilidade, o dia está tranquilo.

Agora mude o *conteúdo* das fotos — de praias para florestas, de estúdio para
rua à noite — e mantenha o mesmo endpoint. O HTTP continua verde. A latência
continua aceitável. O que mudou foi o **mundo** que chega ao modelo.

O caminho completo leva até a pergunta operacional:

> as luminâncias dos pixels que estão chegando ainda se parecem com as do
> treino?

A resposta passa por histograma, CDF, distância vertical δ e a estatística
de Kolmogorov–Smirnov **D**. Quando **D** cruza um limiar, o painel mostra
**ALERTA**.

![Fluxo L → histograma → CDF → δ → D → alerta](illustrations/01_workflow_l_to_alert.png)

---

## 2. DevOps: o serviço que responde

DevOps, neste contexto de aula, é a disciplina de *colocar um processo no
ar e mantê-lo utilizável*: empacotar, servir, receber pedidos, devolver
respostas e saber se a máquina ainda está viva.

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

Nesta pasta, o serviço BentoML expõe rotas de inferência
(`/inference-grayscale`, entre outras). Mais adiante você sobe e exercita
esse serviço com as receitas `just` desta pasta.

---

## 3. MLOps: servir o modelo e observar o mundo

MLOps estende o ciclo de servir: além de “a API responde?”, aparece “os
dados e o comportamento do modelo ainda fazem sentido?”.

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

Três ideias que esta lição amarra:

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

Separar duas camadas evita o falso conforto do “tudo verde”.

**Saúde do serviço.** Porta aberta, processo vivo, respostas 200 (ou
códigos esperados), latência dentro do orçamento, sem exceções em cascata.

**Adequação dos dados.** As imagens de produção ainda se parecem, em
distribuição, com o treino? A estatística **D** (forma de **L**) está
abaixo do limiar de alerta? Há imagens suficientes no lote para a
comparação ser legível?

Um serviço pode estar saudável em HTTP e desalinhado nos dados ao mesmo
tempo: status 200 rápido sobre fotos de um domínio que o treino quase não
viu. A latência mede **espera**. A estatística **D** mede **afastamento de
forma** entre a CDF de luminância da referência e a do lote. O alerta
responde a **D**.

---

## 5. BentoML: colocar a API no ar

BentoML empacota o código de inferência e sobe um servidor HTTP com rotas
tipadas — o mesmo padrão enxuto que aparece em deployments reais.

Nesta lição, a classe de serviço (`service.py`) registra, entre outras, a
rota `/inference-grayscale`. Em linhas gerais:

1. O cliente envia uma imagem.
2. O serviço **registra** features da imagem (log de pedido).
3. O serviço aplica a conversão a cinza e devolve a imagem processada.

```bash
cd 003_ks_drift_alert_streamlit
just sync
just serve
# terminal dedicado: API na porta 3333
```

Enquanto o servidor está no ar, outro terminal pode enviar um tema de
amostras (`just exercise-theme …`) e depois agregar o log
(`just snapshot-batch …`). O Streamlit (`just streamlit`, porta 8503) lê
o corpus de referência e o lote agregado.

**Servir** e **observar** andam juntos. A resposta HTTP é o produto
imediato; o log é a matéria-prima do monitoramento de dados.

---

## 6. Registro de pedidos

Sem vestígio do que chegou, só resta a saúde HTTP. Com log de features,
dá para reconstruir a distribuição de produção.

Cada chamada a `/inference-grayscale` grava um JSON em `request_features/`
(timestamp + id, histogramas de canais, metadados). Depois, um *snapshot*
agrega esses arquivos em `batch_stats/<nome>.json`.

```text
POST /inference-grayscale
  → log JSON em request_features/
  → resposta = imagem em cinza

snapshot-batch
  → soma histogramas do log
  → batch_stats/<lote>.json
  → limpa (ou prepara) a pasta de log para o próximo exercício
```

O painel em [`app.py`](app.py) compara `corpus_stats.json` (referência de
treino) com o JSON do lote escolhido na barra lateral.

Há também um caminho **offline**: `just build-demo-batches` materializa
lotes de demonstração sem precisar do servidor no ar. Serve para estudar
histograma → CDF → **D** com números estáveis.

---

## 7. Imagens, pixels e luminância L

Uma fotografia digital é uma grade de pontos — os **pixels**. Em cores,
cada pixel costuma carregar três canais (vermelho, verde, azul). Para
falar de “quão claro ou escuro” é o ponto, convertemos a imagem para tons
de cinza: preto num extremo, branco no outro, e uma escada de cinzas no
meio.

Na prática isso é `Image.convert("L")` no Pillow. Cada pixel passa a um
inteiro de **0** (preto) a **255** (branco). Chamamos esse valor de
**luminância** e o denotamos por **L**.

Se $I$ é a imagem e $(u,v)$ um sítio na grade,

$$
L(u,v) \in \{0,1,\ldots,255\}
$$

é a intensidade nesse sítio. Tudo o que esta aula desenha e compara —
histograma, CDF, estatística KS — descreve a **distribuição de L sobre os
pixels** do conjunto de imagens. Não usamos a média de L por foto como
eixo: uma média por imagem comprime demais a forma e, no controle de mesmo
tema, pode disparar alerta à toa (detalhe em
[`docs/notas-experimento-freeze.md`](docs/notas-experimento-freeze.md)).

```python
from PIL import Image

img = Image.open("foto.jpg").convert("L")
contagens = img.histogram()  # 256 faixas: quantos pixels têm cada L
```

---

## 8. Histograma

Com L em mão, a pergunta seguinte é: *em cada degrau de cinza, quantos
pixels caíram?* Essa contagem, faixa a faixa, é o **histograma**.

Imagine 256 baldes alinhados do preto ao branco. Cada pixel do conjunto
(todas as imagens da referência, ou todas do lote) cai num balde. A altura
do balde $k$ é a contagem $h_k$. O total de pixels no conjunto é

$$
N = \sum_{k=0}^{B-1} h_k,
$$

com $B = 256$ no freeze padrão (o Streamlit deixa variar o número de
faixas). Em notação de conjunto,

$$
h_k = \lvert\{\text{pixels com } L \text{ na faixa } k\}\rvert.
$$

Para várias imagens, some os histogramas imagem a imagem: o resultado é o
histograma do **conjunto**. O $h_k$ agregado é a soma dos $h_k$
individuais, e $N$ passa a ser o total de pixels do conjunto.

O Streamlit permite reagrupar faixas (16 a 256) para visualizar a mesma
comparação em resoluções diferentes; a definição de **D** permanece a
mesma na grade escolhida.

![Histograma e CDF — exemplo mínimo](illustrations/02_hist_to_cdf_toy.png)

---

## 9. Função de distribuição acumulada (CDF)

O histograma ainda fala em “quantos”. A **função de distribuição
acumulada** (CDF) fala em “até aqui, que fração do total?”. Você caminha
dos baldes escuros para os claros, vai somando as contagens e divide pelo
total $N$. A curva começa perto de zero e termina em um: nunca desce.

$$
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i
\qquad (k = 0,\ldots,B-1).
$$

Propriedades úteis:

- $F_{-1}$ conceitualmente 0; $F_{B-1} = 1$ (se $N > 0$).
- $F$ é não decrescente.
- Dois conjuntos com o mesmo $N$ e as mesmas contagens têm a mesma
  $F$; o que interessa na comparação é a **forma** de $F$ versus
  $G$ (CDF do lote).

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

$$
\mathbf{h} = [2,\ 1,\ 3].
$$

Então $N = 2+1+3 = 6$ e

$$
\begin{aligned}
F_0 &= \frac{2}{6} = \frac{1}{3}, \\
F_1 &= \frac{2+1}{6} = \frac{3}{6} = \frac{1}{2}, \\
F_2 &= \frac{2+1+3}{6} = \frac{6}{6} = 1.
\end{aligned}
$$

Em lista: CDF = `[2/6, 3/6, 6/6]` — cerca de $0{,}33$, $0{,}50$ e $1$.

Agora compare com um segundo histograma $\mathbf{g} = [1,\ 1,\ 4]$
($N'=6$):

$$
G = \Bigl[\tfrac{1}{6},\ \tfrac{2}{6},\ 1\Bigr].
$$

As distâncias verticais:

$$
\begin{aligned}
\delta_0 &= \lvert F_0 - G_0 \rvert = \lvert 2/6 - 1/6 \rvert = 1/6, \\
\delta_1 &= \lvert 3/6 - 2/6 \rvert = 1/6, \\
\delta_2 &= \lvert 1 - 1 \rvert = 0.
\end{aligned}
$$

Logo

$$
D = \max_k \delta_k = \frac{1}{6} \approx 0{,}1667.
$$

Com a regra $D \ge 0{,}10$, este brinquedo já cairia em **ALERTA**
(supondo amostras grandes o bastante para sair de INCONCLUSIVO — ver o
capítulo do alerta).

---

## 11. Kolmogorov–Smirnov: de δ a D

Queremos um único número que resuma “quão longe estão as duas formas de
luminância”.

Sejam $F$ a CDF da referência (treino) e $G$ a CDF do lote
(produção), ambas na mesma grade de faixas. Defina

$$
\delta_k = \lvert F_k - G_k \rvert,
\qquad
D = \max_{k} \delta_k
= \sup_{x} \lvert F(x) - G(x) \rvert.
$$

Interpretação geométrica: sobreponha as duas curvas CDF; em cada abscissa
de L meça a distância vertical; **D** é o maior desses segmentos. Se as
formas de luminância forem parecidas, $D$ fica pequeno. Se o lote
trouxer outro mundo visual, $D$ sobe — e é sobre **esse** número que a
aula dispara o alerta.

![δ(L) e D = max δ](illustrations/06_delta_d.png)

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
$D = \max |F_a - F_b|$.

### Nota: valor-p

O software ainda calcula um **valor-p** assintótico clássico do teste KS
de duas amostras, com tamanho efetivo baseado no **número de imagens** de
cada lado (pixels da mesma foto **não** são independentes — há sutileza
de graus de liberdade e dependência espacial). Esse valor-p **não** entra
na regra de alerta: trate-o como nota estatística no rodapé do painel, não
como motor do alarme. O alerta responde a **D**.

---

## 12. Alerta sobre D

Transformar a estatística contínua **D** numa decisão operacional legível
no painel.

| Estado | Condição | O que significa | Ação típica |
| :--- | :--- | :--- | :--- |
| **INCONCLUSIVO** | $n_{\mathrm{ref}} \lt 8$ **ou** $n_{\mathrm{lote}} \lt 8$ | Ainda há poucas imagens na comparação | Esperar mais pedidos **na janela** |
| **ALERTA** | ambos $n \ge 8$ e $D \ge 0{,}10$ | Formas de L divergem além do limiar | Investigar tema ou uso; abrir ticket / rule |
| **TRANQUILO** | ambos $n \ge 8$ e $D \lt 0{,}10$ | Lote compatível com a referência nesta métrica | Seguir monitorando a janela |

O limiar $0{,}10$ é uma escolha de handout: simples de memorizar e
alinhada à ordem de grandeza do experimento praias × florestas
($D \approx 0{,}23$) versus o controle de mesmo tema
($D \approx 0{,}05$). Em produção real, o limiar seria calibrado ao
risco do negócio e à variabilidade histórica. O que importa na prática da
aula: **o alarme dispara sobre D**.

---

## 13. Janela temporal no monitoramento

Em produção, “o lote” quase nunca é “todas as imagens desde o início dos
tempos”. Monitoramento de dados trabalha com **janelas**.

Fixe:

- **Referência** — corpus de treino (ou um baseline estável revisado
  periodicamente).
- **Janela de produção** — por exemplo, os pedidos dos **últimos 30
  dias** (ou 7 dias, ou a última semana calendário — o número é uma
  política).

Compare a CDF agregada da referência com a CDF agregada **somente** dos
pedidos dentro da janela. O **D** passa a responder:

> nos últimos 30 dias, a forma de L ainda combina com o treino?

| Aspecto | Efeito da janela |
| :--- | :--- |
| Relevância | o alerta reflete o presente operacional |
| Volume | evita diluir um desvio recente numa história antiga enorme |
| Operação | times sabem o período sob escrutínio |
| Reprocessamento | snapshots podem ser refeitos por calendário |

No exercício desta aula, a “janela” é o lote que você monta de propósito
(`forests`, `control`, etc.): um conjunto fechado e nomeado. Em um
sistema real com timestamps no log (`logged_at` nos JSON de
`request_features/`), a agregação filtraria

$$
\{\text{pedidos com } t_{\text{agora}} - 30\text{ dias} \le t_{\text{log}} \le t_{\text{agora}}\}.
$$

O cálculo matemático (histograma → CDF → δ → **D**) é o mesmo; muda só
**quais** imagens entram no histograma do lado produção.

**Política mínima sugerida (estudo).** Escolher a duração da janela (ex.:
30 dias); agregar histogramas só dessa fatia; exigir um mínimo de imagens
(nesta aula: 8) antes de sair de INCONCLUSIVO; alertar se
$D \ge \text{limiar}$; revisar a referência quando o negócio mudar de
domínio de propósito (novo produto visual, nova câmera, novo mercado).

---

## 14. Limiares de D / KS em outros contextos

Não existe um único “D mágico” para o planeta. Em estatística clássica, o
teste de duas amostras pergunta se duas amostras podem ter vindo da mesma
distribuição contínua. Para amostras grandes, rejeita-se essa hipótese ao
nível $\alpha$ quando

$$
D > c(\alpha)\,\sqrt{\frac{n+m}{nm}},
\qquad
c(0{,}05)\approx 1{,}358
$$

([Wikipédia — Kolmogorov–Smirnov](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)).
Com $n = m = 50$, isso pede $D$ acima de cerca de $0{,}27$. Softwares e
tabelas publicam os mesmos cortes para $n$ pequenos
([MetricGate](https://metricgate.com/docs/kolmogorov-smirnov-critical-values/),
[Real Statistics](https://real-statistics.com/statistics-tables/two-sample-kolmogorov-smirnov-table/)).

Em astronomia e ciências experimentais, muitas vezes se consulta uma tabela
de valores críticos $mnD$ para pares $(m,n)$ e $\alpha$ fixos
([NED / Wall](https://ned.ipac.caltech.edu/level5/Wall2/TableA_8.html)): o
espírito é o mesmo (quando $D$ é “grande demais” sob a hipótese nula), mas
o número sai de uma grade pré-computada.

No risco de mercado (FRTB, atribuição de P&L), o KS compara curvas de
lucro/prejuízo hipotético e teórico ao longo de 250 dias. O regulador
desenhou um semáforo em cima do próprio $D$: zona verde abaixo de
**0,09**, vermelha acima de **0,12**, âmbar no meio
([MathWorks](https://www.mathworks.com/help/risk/profit-and-loss-attribution-workflow.html);
[Regulamento Delegado (UE) 2022/2059, art. 8](https://judict.eu/en/sla/32013R0575/32022R2059-X/article-8)).
Aqui o limiar é **política**, não um $\alpha$ de livro-texto.

No *credit scoring*, o KS aparece com outro papel: mede o **poder de
separação** entre clientes que deram default e os que não deram. Quanto
**maior** o KS entre as duas curvas de score, melhor o modelo discrimina
([SAS Model Manager](https://support.sas.com/documentation/cdl/en/mdlmgrug/69919/HTML/default/n194xndt3b3y1pn1ufc0mqbsmht4.htm)).
Não se trata de “as distribuições são iguais?”; trata-se de “as curvas
estão bem afastadas?”.

| Área | Papel do KS | Regra típica | Fonte |
| :--- | :--- | :--- | :--- |
| Estatística (duas amostras) | Teste de igualdade de distribuições | $D > c(\alpha)\sqrt{(n+m)/(nm)}$ | [Wikipédia](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test) |
| Tabelas / software | Idem, $n$ pequenos | Valores críticos tabulados | [MetricGate](https://metricgate.com/docs/kolmogorov-smirnov-critical-values/); [Real Statistics](https://real-statistics.com/statistics-tables/two-sample-kolmogorov-smirnov-table/) |
| Astronomia / ciências | Idem via tabela $mnD$ | Cortes por $(m,n),\alpha$ | [NED / Wall](https://ned.ipac.caltech.edu/level5/Wall2/TableA_8.html) |
| FRTB P&L | Semáforo regulatório sobre $D$ | verde &lt; 0,09; vermelho &gt; 0,12 | [MathWorks](https://www.mathworks.com/help/risk/profit-and-loss-attribution-workflow.html); [UE 2022/2059](https://judict.eu/en/sla/32013R0575/32022R2059-X/article-8) |
| Credit scoring | Discriminação default vs non-default | KS alto = melhor separação | [SAS](https://support.sas.com/documentation/cdl/en/mdlmgrug/69919/HTML/default/n194xndt3b3y1pn1ufc0mqbsmht4.htm) |

---

## 15. O experimento desta aula

**Objetivo operacional.**

1. Fixar um tema como referência de treino (sem rede neural).
2. Enviar outro tema (ou o mesmo) por `/inference-grayscale` com log.
3. No Streamlit, construir histograma → CDF → δ → **D** e ler o alerta
   sobre **D**.

**Desenho.** Tema de referência = primeiras 50 praias
(`samples/beaches/`) → `corpus_stats.json`. Lotes offline típicos
(`just build-demo-batches`):

- `batch_stats/control.json` — praias 51–100 (mesmo tema, outro trecho).
- `batch_stats/forests.json` — 50 florestas.

| Comparação | $D$ típico | Alerta ($D \ge 0{,}10$) |
| :--- | :--- | :--- |
| praias[:50] vs florestas[:50] | $\approx 0{,}23$ | ALERTA |
| praias[:50] vs praias[50:100] | $\approx 0{,}05$ | TRANQUILO |

| Histograma (treino) | Histograma (lote) |
| :---: | :---: |
| ![hist praias](illustrations/03_hist_beaches.png) | ![hist florestas](illustrations/04_hist_forests.png) |

![Duas CDFs com segmento em D](illustrations/05_dual_cdf.png)

Por que 50 imagens (e não as 110 do tema), e por que L por pixel em vez
da média por imagem: ver
[`docs/notas-experimento-freeze.md`](docs/notas-experimento-freeze.md).

A base só devolve a imagem filtrada. Esta lição grava o pedido (como a
linha `020`) e analisa a distribuição de **L** no Streamlit.

---

## 16. Estrutura da pasta

```text
003_ks_drift_alert_streamlit/
  README.md                 # handout da lição
  app.py                    # Streamlit: defs + gráficos + alerta sobre D
  service.py                # BentoML /inference-grayscale + log
  banner.py                 # alert_on_d (D≥0,10) + regra legada com valor-p
  ks_compare.py             # D, CDFs, contagens entre referência e lote
  histogram.py              # L, histograma, CDF
  corpus_stats.py           # agrega features/ → estatística de treino
  request_stats.py          # agrega request_features/ → lote
  request_log.py            # grava JSON em request_features/
  plotting.py               # histograma, CDF, δ, dual CDF
  corpus_stats.json         # freeze: praias[:50]
  batch_stats/              # control.json, forests.json, …
  request_features/         # log vivo (gitkeep; JSON ignorados)
  features/                 # saídas de extract
  illustrations/            # PNGs do handout (just generate-illustrations)
  scripts/
    extract_image_features.py   # praias[:50] → features/
    build_corpus_stats.py       # features/ → corpus_stats.json
    build_batch_from_theme.py   # tema → batch_stats/<nome>.json (offline)
    exercise_theme.py           # POST tema no serviço → request_features/
    snapshot_batch.py           # request_features/ → batch_stats/
    generate_illustrations.py   # regenera illustrations/
    verify_ks_banner.py         # imprime D/alerta sem UI
  tests/                    # pytest
  docs/
    meta-da-aula-a-formula.md   # cartão-resumo da fórmula
    notas-experimento-freeze.md # por que 50; pixel vs média
  justfile
```

| Artefato | Papel |
| :--- | :--- |
| `service.py` | API BentoML; log em `/inference-grayscale` |
| `request_log.py` | grava JSON em `request_features/` |
| `histogram.py` | histograma e CDF |
| `ks_compare.py` | $D$ (e valor-p assintótico, nota de rodapé) |
| `banner.py` | regra INCONCLUSIVO / ALERTA / TRANQUILO sobre **D** |
| `app.py` | painel Streamlit |
| `corpus_stats.json` | referência agregada de treino |
| `batch_stats/*.json` | lotes agregados |
| `illustrations/` | figuras do handout e do app |

---

## 17. Como executar

### Caminho offline (lotes já materializados, sem servidor)

```bash
cd 003_ks_drift_alert_streamlit
# entra na pasta da lição

just sync
# cria/atualiza .venv e instala dependências do pyproject (uv)

just download-samples
# aponta para samples/{beaches,forests,balls}/ na raiz do repositório
# (não baixa de novo se o corpus temático já estiver lá)

just extract-features
# extrai histograma L (e canais) das primeiras 50 praias → features/*.json

just build-corpus-stats
# agrega features/ → corpus_stats.json (referência de treino)

just build-demo-batches
# grava batch_stats/control.json (praias 51–100) e batch_stats/forests.json
# (50 florestas), sem precisar do BentoML no ar

just generate-illustrations
# opcional: regenera illustrations/*.png usadas neste handout

just streamlit
# sobe o app em http://localhost:8503
```

### Caminho com servidor (log real em `request_features/`)

```bash
just serve
# terminal 1: BentoML com /inference-grayscale na porta 3333

just clear-request-features
# apaga JSON antigos em request_features/ para o próximo exercício

just exercise-theme forests
# POST de imagens de samples/forests/ no serviço; cada pedido vira um JSON
# de features em request_features/

just snapshot-batch forests
# agrega request_features/ → batch_stats/forests.json e limpa a pasta de log

just clear-request-features
# prepara a pasta de log para o lote de controle

just exercise-theme beaches --offset=12 --count=12
# envia 12 praias (a partir da 13ª) como “produção” de mesmo tema

just snapshot-batch control
# agrega esse log → batch_stats/control.json

just streamlit
# compara corpus_stats.json com o lote escolhido na barra lateral
```

### O que acontece por dentro

```text
imagem → convert("L") → histograma de L (pixels)
beaches[:50] → soma → corpus_stats.json
lote → /inference-grayscale → request_features/ → batch_stats/
app: histograma → CDF → δ → D → alerta se D ≥ 0,10
```

---

## 18. Glossário

| Termo | Significado nesta aula |
| :--- | :--- |
| **L** | luminância do pixel após `convert("L")`, em $\{0,\ldots,255\}$ |
| **Histograma** | contagens $h_k$ por faixa de L |
| **CDF** | $F_k = (1/N)\sum_{i\le k} h_i$ |
| **δ** | $\lvert F_k - G_k \rvert$ |
| **D** | $\max_k \delta_k$ (Kolmogorov–Smirnov) |
| **Referência / corpus** | distribuição de treino agregada |
| **Lote / produção** | agregação de pedidos (ou batch demo) |
| **ALERTA** | $D \ge 0{,}10$ com amostras suficientes |
| **Janela temporal** | fatia de pedidos (ex.: últimos 30 dias) usada no lote |

Cartão-resumo ainda mais curto:
[`docs/meta-da-aula-a-formula.md`](docs/meta-da-aula-a-formula.md).

---

## 19. Testes

```bash
just test
```

---

## 20. Bibliografia

1. [Kolmogorov–Smirnov (Wikipédia)](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)
2. Gama et al., *A survey on concept drift adaptation*, ACM CSUR 2014 —
   [doi:10.1145/2523813](https://doi.org/10.1145/2523813)
3. [PSI — KAscore Ongoing Monitoring](https://ketchbrookanalytics.github.io/KAscore/articles/ongoing-monitoring.html)
4. Taplin & Hunt, Risks 2019 — [MDPI](https://www.mdpi.com/2227-9091/7/2/53)
5. [Pillow — Image](https://pillow.readthedocs.io/en/stable/reference/Image.html)
6. Limiares FRTB / crédito: ver links na
   [seção 14](#14-limiares-de-d--ks-em-outros-contextos)

[`004_prometheus_histcdf_streamlit`](../004_prometheus_histcdf_streamlit/README.md)
