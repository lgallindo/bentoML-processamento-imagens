"""Streamlit: histograma → CDF → KS da luminância L; alerta sobre D."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st
from PIL import Image

from banner import alert_on_d
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

LOTE_ROTULO = {
    "control": "Mesmo tema (outro trecho de praias)",
    "forests": "Florestas",
    "beaches": "Praias",
    "balls": "Bolas",
    "landscapes": "Mistura praias e florestas",
}

POC_L = '''from PIL import Image

img = Image.open("foto.jpg").convert("L")  # L ∈ {0, …, 255} por pixel
contagens = img.histogram()
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

st.header("Definições")

st.subheader("L — luminância do pixel")
st.markdown(
    r"""
**Didática.** Cada pixel vira um tom de cinza: 0 = preto, 255 = branco.

**Formal.** Após `Image.convert("L")`, \(L(u,v) \in \{0,\ldots,255\}\).
O eixo das distribuições é **L por pixel**, não a média de L por imagem
(médias geram falso alerta no controle de mesmo tema).
"""
)
st.code(POC_L, language="python")

st.subheader("Histograma")
st.markdown(
    r"""
**Didática.** Conta quantos pixels caíram em cada faixa de L.

**Formal.** \(h_k\) = número de pixels na faixa \(k\),
\(N = \sum_k h_k\). Para um conjunto de imagens, some os histogramas.
"""
)

st.subheader("CDF")
st.markdown(
    r"""
**Didática.** Em cada faixa: *até aqui, que fração dos pixels já passou?*
A curva sobe de 0 a 1.

**Formal.**
$$
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i.
$$

**Exemplo mínimo** — contagens `[2, 1, 3]` (\(N=6\)) →
CDF `[2/6, 3/6, 6/6]`.
"""
)
toy = fig("02_hist_to_cdf_toy.png")
if toy:
    st.image(str(toy), caption="Do histograma à CDF — exemplo mínimo")
st.code(ALGORITMO_CDF, language="text")

st.subheader("δ e D")
st.markdown(
    r"""
**Didática.** Compare a CDF da referência \(F\) com a do lote \(G\). Em cada
faixa, a distância vertical é \(\delta\). **D** é a maior dessas distâncias.

**Formal.**
$$
\delta_k = |F_k - G_k|,
\qquad
D = \max_k \delta_k.
$$

**Alerta sobre D** (regra desta aula + time boxing):

| Estado | Condição | Leitura |
| :--- | :--- | :--- |
| INCONCLUSIVO | n &lt; 8 em qualquer lado | Janela / lote ainda fino |
| ALERTA | n ≥ 8 e D ≥ 0,10 | Formas de L divergem |
| TRANQUILO | n ≥ 8 e D &lt; 0,10 | Compatível com a referência |

Em produção o lote é uma **caixa de tempo** (ex.: pedidos dos **últimos
30 dias**), não o histórico inteiro.
"""
)

batches = list_batches()
if not batches:
    st.warning(
        "Não há arquivos em `batch_stats/`. "
        "Rode `just build-demo-batches` ou "
        "`just exercise-theme` + `just snapshot-batch`."
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
    "Há complexidades de graus de liberdade / dependência entre pixels da "
    "mesma foto; o alerta desta aula responde só a **D**, não ao valor-p."
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
