"""Streamlit: histograma → CDF → KS da luminância L entre referência e lote."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st
from PIL import Image

from banner import banner_rule
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

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"

BANNER_PT = {
    "ALERT": "ALERTA",
    "WATCH": "SINAL PARCIAL",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}

ALGORITMO_CDF = """\
# Variáveis:
# contagens — lista de inteiros do histograma de L (passo 1)
# total — soma(contagens) = número de pixels no conjunto
# acumulado — soma parcial ao percorrer as faixas
# cdf — lista de F(L) em [0, 1], uma entrada por faixa
# c — contagem da faixa corrente

total ← soma(contagens)
acumulado ← 0
cdf ← lista vazia
para cada c em contagens:
    acumulado ← acumulado + c
    acrescentar (acumulado / total) em cdf
# cdf[i] = fração dos pixels com L na faixa i ou mais escura
"""

ALGORITMO_DELTA = """\
# Variáveis:
# F_ref — CDF de L do conjunto de referência (passo 2)
# F_lote — CDF de L do lote atual (passo 2)
# i — índice da faixa (mesmo eixo de L nas duas CDFs)
# delta — lista δ(i) = |F_ref[i] − F_lote[i]|
# D — estatística de Kolmogorov–Smirnov (= máximo de delta)
# i_star — faixa onde delta atinge o máximo

delta ← lista vazia
para i de 0 até comprimento(F_ref) − 1:
    acrescentar |F_ref[i] − F_lote[i]| em delta
D ← máximo(delta)
i_star ← argmáximo(delta)
# O gráfico abaixo é delta; a linha tracejada é D.
"""

LOTE_ROTULO = {
    "control": "Mesmo tema (outro trecho de praias)",
    "forests": "Florestas",
    "beaches": "Praias",
    "balls": "Bolas",
    "landscapes": "Mistura praias e florestas",
}

POC_L = '''from PIL import Image

img = Image.open("foto.jpg").convert("L")  # cada pixel → L ∈ {0, …, 255}
contagens = img.histogram()               # 256 faixas: quantos pixels têm cada L
# A distribuição nesta aula é a de L sobre os pixels (somando várias imagens).
'''


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def list_batches() -> list[str]:
    if not BATCH_STATS_DIR.is_dir():
        return []
    return sorted(p.stem for p in BATCH_STATS_DIR.glob("*.json"))


def rotulo_lote(name: str) -> str:
    if name in LOTE_ROTULO:
        return LOTE_ROTULO[name]
    if name.startswith("beaches+"):
        return "Mistura de temas"
    return name


def theme_paths_for_batch(name: str) -> list[Path]:
    root = repo_root() / "samples"
    mapping = {
        "forests": root / "forests",
        "control": root / "beaches",
        "beaches": root / "beaches",
        "balls": root / "balls",
        "landscapes": None,
    }
    if name == "landscapes" or name.startswith("beaches+"):
        return sorted((root / "beaches").glob("*.jpg"))[:4] + sorted(
            (root / "forests").glob("*.jpg")
        )[:4]
    folder = mapping.get(name, root / name)
    if folder is None or not folder.is_dir():
        return []
    return sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))


def caminhos_referencia() -> list[Path]:
    root = repo_root() / "samples" / "beaches"
    return sorted(root.glob("*.jpg")) + sorted(root.glob("*.jpeg"))


def mostrar_amostra(caminho: Path | None, legenda: str) -> None:
    if caminho is None or not caminho.is_file():
        st.caption("(sem imagem de amostra)")
        return
    st.image(Image.open(caminho), caption=legenda, width=220)


st.set_page_config(page_title="Alerta KS de drift", layout="wide")
st.title("Alerta KS de drift")

st.markdown(
    """
### Meta desta aula

O serviço pode responder bem e mesmo assim estar **descasado dos dados** que
chegam — outro tema de imagem, outro uso do modelo. Latência sozinha não
conta essa história. Aqui medimos o afastamento na **forma** dos dados e
ligamos isso a um **alerta** sobre a estatística de Kolmogorov–Smirnov (**D**):
o mesmo gesto que, em produção, alimentaria uma rule de monitoramento.

**Como:** comparamos a distribuição de luminância **L** da referência com a
do lote; montamos as CDFs; calculamos **δ = |F_ref − F_lote|**; tomamos
**D = max δ**; o banner reage a **D** e ao valor-p.

### Variável sob estudo: **L** (luminância de **cada pixel**)

O eixo X **não** é a luminância média da imagem. É o valor de cinza de
**cada pixel** após `Image.convert("L")`: inteiro **0** (preto) … **255**
(branco). Histograma, CDF e KS agregam **pixels** do conjunto — não médias
por foto, nem RGB canal a canal.
"""
)

st.code(POC_L, language="python")

batches = list_batches()
if not batches:
    st.warning(
        "Não há arquivos em `batch_stats/`. "
        "Rode `just build-demo-batches` (offline) ou "
        "`just exercise-theme` + `just snapshot-batch` com o servidor no ar."
    )
    st.stop()

with st.sidebar:
    st.header("Parâmetros")
    batch_name = st.selectbox(
        "Lote atual",
        batches,
        format_func=rotulo_lote,
    )
    n_intervalos = st.slider(
        "Número de faixas do histograma de L",
        min_value=16,
        max_value=256,
        value=256,
        step=16,
        help="Quantas faixas usamos ao agrupar os valores de L dos pixels.",
    )

referencia = load_default_corpus_stats()
lote = load_request_stats(BATCH_STATS_DIR / f"{batch_name}.json")
payload = compare_stats(referencia, lote, channel="L", bins=n_intervalos)
estado = banner_rule(
    payload["p_value"],
    payload["statistic"],
    payload["n_images_corpus"],
    payload["n_images_production"],
)

cores = {
    "ALERT": "#c62828",
    "WATCH": "#ef6c00",
    "QUIET": "#2e7d32",
    "INCONCLUSIVE": "#546e7a",
}
st.markdown(
    f"<div style='padding:1rem;border-radius:8px;background:{cores[estado]};"
    f"color:white;font-size:1.4rem;font-weight:600'>{BANNER_PT[estado]}</div>",
    unsafe_allow_html=True,
)

m1, m2 = st.columns(2)
m1.metric("D (KS sobre L)", f"{payload['statistic']:.4f}")
m2.metric("valor-p", f"{payload['p_value']:.4g}")

label_ref = "referência (praias de treino)"
label_lote = rotulo_lote(batch_name)
amostra_ref = caminhos_referencia()[:1]
amostra_lote = theme_paths_for_batch(batch_name)[:1]

st.header("1. Histograma de L em cada conjunto")
st.markdown(
    """
Para cada imagem, `convert("L")` + `histogram()` conta quantos pixels caem
em cada valor de **L**. Somamos essas contagens em todas as imagens do
conjunto. As barras abaixo são essa soma: a forma da distribuição de
**L** (brilho dos pixels) na referência e no lote.
"""
)
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
st.markdown(
    """
Do histograma do passo 1 para a CDF: percorra as faixas da esquerda para a
direita, some as contagens e normalize pelo total de pixels. Em cada faixa,
**F(L)** = fração dos pixels com luminância ≤ aquela faixa. Duas CDFs iguais
⇒ mesma distribuição de L; o máximo de |F_ref − F_lote| é **D** do KS.
"""
)
st.markdown("**Algoritmo (rascunho) — histograma → CDF**")
st.code(ALGORITMO_CDF, language="text")
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

st.header("3. As duas CDFs de L no mesmo gráfico")
st.markdown(
    """
Sobrepondo as curvas de **L**, o segmento vermelho vertical marca o ponto em
que |F_ref − F_lote| é máximo — esse comprimento é a estatística **D** do KS.
O banner resume **D** e o valor-p (ALERTA / SINAL PARCIAL / TRANQUILO /
INCONCLUSIVO).
"""
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

st.header("4. Diferença absoluta entre as CDFs")
st.markdown(
    """
Definimos a função **δ(L) = |F_ref(L) − F_lote(L)|** na mesma grade de faixas.
O gráfico é δ; a linha tracejada e o ponto vermelho são
**D = max δ(L)** — a estatística de Kolmogorov–Smirnov usada no banner.
"""
)
st.markdown("**Algoritmo (rascunho) — duas CDFs → δ → D**")
st.code(ALGORITMO_DELTA, language="text")
st.pyplot(
    plot_cdf_abs_diff(
        payload["cdf_corpus"],
        payload["cdf_production"],
        title="δ(L) = |F_ref(L) − F_lote(L)|",
    )
)

st.subheader("Miniaturas")
box_treino, box_lote = st.columns(2)
with box_treino:
    with st.container(border=True):
        st.markdown("**Conjunto de treino (referência)**")
        thumbs_treino = load_thumbnails(caminhos_referencia())
        if thumbs_treino:
            st.image(thumbs_treino, width=96)
        else:
            st.caption("Sem imagens de treino.")
with box_lote:
    with st.container(border=True):
        st.markdown(f"**Lote atual — {label_lote}**")
        thumbs_lote = load_thumbnails(theme_paths_for_batch(batch_name))
        if thumbs_lote:
            st.image(thumbs_lote, width=96)
        else:
            st.caption("Sem imagens neste lote.")

with st.expander("Detalhe numérico do KS"):
    visivel = {
        k: v
        for k, v in payload.items()
        if not k.startswith("cdf") and not k.startswith("counts")
    }
    st.code(json.dumps(visivel, indent=2, ensure_ascii=False))
