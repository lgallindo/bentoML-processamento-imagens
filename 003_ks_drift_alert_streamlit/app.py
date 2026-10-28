"""Painel Streamlit da aula 003: L → histograma → CDF → D → alerta.

Orquestra o ritual didático (defs, amostras, gráficos e estado do alerta)
sobre lotes offline em batch_stats/ comparados ao corpus de referência.

Pré-condições:
  - pasta batch_stats/ existe e contém JSON de lotes;
  - corpus_stats.json carregável via load_default_corpus_stats();
  - samples/beaches (e temas dos lotes) existem na raiz do repositório Git.

Fluxo::

    lote JSON ──► compare_stats ──► D, CDFs, contagens
         │                              │
         └─► thumbs / plots ◄───────────┤
                                        └─► alert_on_d → ALERTA|TRANQUILO|INCONCLUSIVO

Saídas principais: UI Streamlit (sem API); estado do alerta em português.
"""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
from PIL import Image

from alert_rule import alert_on_d
from corpus_stats import load_default_corpus_stats
from ks_compare import compare_stats
from plotting import (
    load_thumbnails,
    plot_cdf,
    plot_cdf_abs_diff,
    plot_dual_cdf,
    plot_histogram,
)
from request_stats import load_request_stats
from sample_sets import (
    caminhos_referencia,
    list_batch_names,
    rotulo_lote,
    theme_paths_for_batch,
)
from workflow_boxes import SNIPPETS

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"
ILLUSTRATIONS = ROOT / "illustrations"

ALERTA_PT = {
    "ALERT": "ALERTA",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}

ALGORITMO_CDF = """\
# Variáveis:
# contagens — histograma de L
# total — soma(contagens) = número de pixels
# acumulado, cdf, c

total ← soma(contagens)
acumulado ← 0
cdf ← lista vazia
para cada c em contagens:
    acumulado ← acumulado + c
    acrescentar (acumulado / total) em cdf
"""

ALGORITMO_DELTA = """\
# Variáveis:
# F_ref, F_lote — CDFs na mesma grade de L
# delta, D, i_star

delta ← lista vazia
para i de 0 até comprimento(F_ref) − 1:
    acrescentar |F_ref[i] − F_lote[i]| em delta
D ← máximo(delta)
i_star ← argmáximo(delta)
"""

POC_L = '''from PIL import Image

img = Image.open("foto.jpg").convert("L")  # L ∈ {0, …, 255} por pixel
contagens = img.histogram()
'''


def mostrar_amostra(caminho: Path | None, legenda: str) -> None:
    if caminho is None or not caminho.is_file():
        st.caption("(sem imagem de amostra)")
        return
    st.image(Image.open(caminho), caption=legenda, width=220)


def fig(name: str) -> Path | None:
    path = ILLUSTRATIONS / name
    return path if path.is_file() else None


st.set_page_config(page_title="Alerta KS de drift", layout="wide")
st.title("Alerta KS de drift")

st.header("Meta desta aula")
st.markdown(
    """
Este serviço pode responder **rápido** e com **HTTP 200** e, mesmo assim,
trabalhar sobre um mundo diferente do treino: outro tema de foto, outro
padrão de uso do modelo. A latência mede espera. Ela não mede se os
**dados** ainda combinam com a referência.

Aqui você mede essa combinação na **forma** da distribuição de luminância
**L**, resume o afastamento numa estatística **D** (Kolmogorov–Smirnov) e
produz um **alerta** quando **D** cruza um limiar.
"""
)
fluxo = fig("01_workflow_l_to_alert.png")
if fluxo:
    st.image(str(fluxo), caption="Fluxo: L → histograma → CDF → δ → D → alerta")

with st.expander("Uma caixa por vez — código e script"):
    st.caption(
        "Mesmas caixas do fluxo acima; handout §1.1–1.6. "
        "Scripts isolados em scripts/workflow_boxes/."
    )
    ordem = [
        ("L (pixel)", "illustrations/box_01_l_pixel.png", "scripts/workflow_boxes/box_01_luminancia.py"),
        ("histograma h", "illustrations/box_02_histograma_h.png", "scripts/workflow_boxes/box_02_histograma.py"),
        ("CDF F", "illustrations/box_03_cdf_f.png", "scripts/workflow_boxes/box_03_cdf.py"),
        ("δ = |F − G|", "illustrations/box_04_delta.png", "scripts/workflow_boxes/box_04_delta.py"),
        ("D = max δ", "illustrations/box_05_d_max.png", "scripts/workflow_boxes/box_05_d_max.py"),
        ("alerta em D", "illustrations/box_06_alerta_d.png", "scripts/workflow_boxes/box_06_alerta.py"),
    ]
    for titulo, png, script in ordem:
        st.markdown(f"**{titulo}** — `{script}`")
        p = ROOT / png
        if p.is_file():
            st.image(str(p), width=160)
        st.code(SNIPPETS[titulo], language="python")

st.header("Como usar este painel")
st.markdown(
    r"""
Siga a ordem abaixo. A **barra lateral** só escolhe parâmetros; a leitura
e o ritual ficam neste corpo da página.

**Passo 1 — Controles (barra lateral).** Escolha o **Lote atual** (lado
produção da comparação KS). A referência de treino é **fixa**: as primeiras
50 praias em `corpus_stats.json`. Opcionalmente ajuste o **número de faixas**
do histograma de L (padrão **256** = um balde por nível de cinza; valores
menores suavizam a forma e podem alterar um pouco **D**, sem mudar a regra
de alerta).

**Passo 2 — O que cada lote significa.** Cada opção é um JSON em
`batch_stats/`:

- **Mesmo tema (outro trecho de praias)** — controle: praias
  `[50:100]`, **disjuntas** do treino `[:50]`. Espera-se **TRANQUILO**
  ($D$ baixo).
- **Florestas** — tema divergente: espera-se **ALERTA**.
- **Bolas** (se existir no disco) — contingência visual: tipicamente
  **ALERTA**.

O lote misto praias+florestas **não** aparece aqui; ele é a aula opcional
`007_ks_mixed_landscape_streamlit`. Um JSON chamado `beaches` (mesma fatia
do treino) também fica de fora, para não comparar o corpus consigo mesmo.

**Passo 3 — Cartão de alerta.** Logo abaixo das definições, leia
**ALERTA** / **TRANQUILO** / **INCONCLUSIVO** e o valor de **D**. O alerta
responde só a **D** (e ao mínimo de imagens); o valor-p é nota de rodapé.

**Passo 4 — Ritual gráfico (seções 1→4).** Desça na página:

1. histograma de L em cada conjunto;
2. CDF de cada lado;
3. as duas CDFs com o segmento **D**;
4. a função $\delta$ e $D = \max \delta$.

**Passo 5 — Miniaturas.** No fim, confira as grades: à esquerda o treino;
à direita o lote. No controle, as fotos **não** devem ser as mesmas do
treino.
"""
)

st.header("Definições")

st.subheader("L — luminância do pixel")
st.markdown(
    r"""
Uma fotografia digital é uma grade de pontos — os **pixels**. Em cores, cada
pixel costuma carregar três canais. Para falar de “quão claro ou escuro” é o
ponto, convertemos a imagem para tons de cinza: preto num extremo, branco no
outro, e uma escada de cinzas no meio.

Na prática isso é `Image.convert("L")` no Pillow. Cada pixel passa a um
inteiro de **0** (preto) a **255** (branco). Chamamos esse valor de
**luminância** e o denotamos por **L**. Se \(I\) é a imagem e \((u,v)\) um
sítio na grade, \(L(u,v) \in \{0,1,\ldots,255\}\).

Tudo o que este app desenha e compara descreve a **distribuição de L sobre
os pixels** do conjunto. O eixo não é a média de L por foto: uma média por
imagem comprime demais a forma e, no controle de mesmo tema, pode disparar
alerta à toa (ver `docs/notas-experimento-freeze.md` no handout).
"""
)
st.code(POC_L, language="python")

st.subheader("Histograma")
st.markdown(
    r"""
Com L em mão, a pergunta seguinte é: *em cada degrau de cinza, quantos
pixels caíram?* Essa contagem, faixa a faixa, é o **histograma**.

Imagine baldes alinhados do preto ao branco. Cada pixel do conjunto cai num
balde. A altura do balde \(k\) é a contagem \(h_k\). O total de pixels é
\(N = \sum_k h_k\). Para várias imagens, some os histogramas imagem a
imagem: o resultado é o histograma do **conjunto**.
"""
)

st.subheader("CDF")
st.markdown(
    r"""
O histograma ainda fala em “quantos”. A **função de distribuição acumulada**
(CDF) fala em “até aqui, que fração do total?”. Você caminha dos baldes
escuros para os claros, vai somando as contagens e divide pelo total \(N\).
A curva começa perto de zero e termina em um: nunca desce.

$$
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i.
$$

**Exemplo mínimo.** Contagens `[2, 1, 3]` (\(N=6\)) → CDF
`[2/6, 3/6, 6/6]` — cerca de \(0{,}33\), \(0{,}50\) e \(1\).
"""
)
toy = fig("02_hist_to_cdf_toy.png")
if toy:
    st.image(str(toy), caption="Do histograma à CDF — exemplo mínimo")
st.code(ALGORITMO_CDF, language="text")

st.subheader("δ e D")
st.markdown(
    r"""
Agora você tem duas curvas na mesma grade de L: \(F\) na referência
(treino) e \(G\) no lote atual. Em cada faixa, a distância vertical entre
elas é \(\delta_k = \lvert F_k - G_k \rvert\). A estatística de
Kolmogorov–Smirnov de duas amostras é o **maior** desses afastamentos:

$$
D = \max_k \delta_k = \sup_x \lvert F(x) - G(x) \rvert.
$$

Se as formas de luminância forem parecidas, \(D\) fica pequeno. Se o lote
trouxer outro mundo visual, \(D\) sobe — e é sobre **esse** número que o
alerta dispara.

| Estado | Condição | Leitura |
| :--- | :--- | :--- |
| INCONCLUSIVO | \(n &lt; 8\) em qualquer lado | Janela / lote ainda fino |
| ALERTA | \(n \ge 8\) e \(D \ge 0{,}10\) | Formas de L divergem |
| TRANQUILO | \(n \ge 8\) e \(D &lt; 0{,}10\) | Compatível com a referência |

Em produção o lote é uma **caixa de tempo** (por exemplo pedidos dos
**últimos 30 dias**), não o histórico desde o dia zero. Sem esse fechamento
temporal, misturam-se regimes antigos e novos e o **D** deixa de responder
à pergunta *“o serviço ainda está adequado ao tráfego recente?”*.
"""
)

batches = list_batch_names(BATCH_STATS_DIR)

with st.sidebar:
    st.header("Controles")
    st.caption("Explicação dos lotes e das faixas: «Como usar este painel».")
    batch_name = st.selectbox(
        "Lote atual",
        batches,
        format_func=rotulo_lote,
        help=(
            "Referência fixa = praias de treino[:50]. O lote é o lado "
            "produção da comparação KS."
        ),
    )
    n_intervalos = st.slider(
        "Número de faixas do histograma de L",
        min_value=16,
        max_value=256,
        value=256,
        step=16,
        help="256 = resolução nativa de L. Menos faixas = histograma mais grosso.",
    )

referencia = load_default_corpus_stats()
lote = load_request_stats(BATCH_STATS_DIR / f"{batch_name}.json")
payload = compare_stats(referencia, lote, channel="L", bins=n_intervalos)
estado = alert_on_d(
    payload["statistic"],
    payload["n_images_corpus"],
    payload["n_images_production"],
)

st.header("Alerta sobre D neste lote")
cores = {
    "ALERT": "#c62828",
    "QUIET": "#2e7d32",
    "INCONCLUSIVE": "#546e7a",
}
st.markdown(
    f"<div style='padding:1rem;border-radius:8px;background:{cores[estado]};"
    f"color:white;font-size:1.4rem;font-weight:600'>"
    f"{ALERTA_PT[estado]} — D = {payload['statistic']:.4f}</div>",
    unsafe_allow_html=True,
)
st.metric("D (Kolmogorov–Smirnov sobre L)", f"{payload['statistic']:.4f}")
st.caption(
    f"Nota: valor-p assintótico ≈ {payload['p_value']:.4g} "
    f"(n efetivo por imagens ≈ {payload['n_eff']:.2f}). "
    "Pixels da mesma foto não são independentes; o alerta responde só a "
    "**D**, não ao valor-p."
)

label_ref = "referência (praias de treino)"
label_lote = rotulo_lote(batch_name)
amostra_ref = caminhos_referencia()[:1]
amostra_lote = theme_paths_for_batch(batch_name)[:1]

st.header("1. Histograma de L em cada conjunto")
col_h1, col_h2 = st.columns(2)
with col_h1:
    mostrar_amostra(
        amostra_ref[0] if amostra_ref else None,
        "Amostra da referência",
    )
    st.pyplot(
        plot_histogram(
            payload["counts_corpus"],
            title="Histograma de L — referência",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with col_h2:
    mostrar_amostra(
        amostra_lote[0] if amostra_lote else None,
        "Amostra do lote",
    )
    st.pyplot(
        plot_histogram(
            payload["counts_production"],
            title="Histograma de L — lote atual",
            series_label=label_lote,
            color="#ef6c00",
        )
    )

st.header("2. CDF de L em cada conjunto")
st.markdown(r"Aplicamos \(F_k = (1/N)\sum_{i\le k} h_i\) a cada lado.")
col_c1, col_c2 = st.columns(2)
with col_c1:
    st.pyplot(
        plot_cdf(
            payload["cdf_corpus"],
            title="CDF de L — referência",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with col_c2:
    st.pyplot(
        plot_cdf(
            payload["cdf_production"],
            title="CDF de L — lote atual",
            series_label=label_lote,
            color="#ef6c00",
        )
    )

st.header("3. As duas CDFs e o segmento D")
st.markdown(
    "O segmento vermelho vertical é **D** = máximo de |F_ref − F_lote|."
)
st.pyplot(
    plot_dual_cdf(
        payload["cdf_corpus"],
        payload["cdf_production"],
        title=f"CDF de L — referência e {label_lote}",
        label_referencia=label_ref,
        label_lote=label_lote,
    )
)

st.header("4. Função δ e D = max δ")
st.code(ALGORITMO_DELTA, language="text")
st.pyplot(
    plot_cdf_abs_diff(
        payload["cdf_corpus"],
        payload["cdf_production"],
        title="δ(L) = |F_ref(L) − F_lote(L)|",
    )
)

st.header("Miniaturas")
box_treino, box_lote = st.columns(2)
with box_treino:
    with st.container(border=True):
        st.markdown("**Conjunto de treino (referência)**")
        thumbs = load_thumbnails(caminhos_referencia())
        if thumbs:
            st.image(thumbs, width=96)
with box_lote:
    with st.container(border=True):
        st.markdown(f"**Lote atual — {label_lote}**")
        thumbs = load_thumbnails(theme_paths_for_batch(batch_name))
        if thumbs:
            st.image(thumbs, width=96)

with st.expander("Detalhe numérico"):
    visivel = {
        k: v
        for k, v in payload.items()
        if not k.startswith("cdf") and not k.startswith("counts")
    }
    st.code(json.dumps(visivel, indent=2, ensure_ascii=False))
