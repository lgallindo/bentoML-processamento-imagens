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
from plotting import load_thumbnails, plot_cdf, plot_dual_cdf, plot_histogram
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"

BANNER_PT = {
    "ALERT": "ALERTA",
    "WATCH": "ATENÇÃO",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}

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
### Variável sob estudo: **L** (luminância de cada pixel)

**L** é o valor de cinza do pixel depois de `Image.convert("L")`: um inteiro
de **0** (preto) a **255** (branco). O histograma, a CDF e o KS desta aula
descrevem a **distribuição de L sobre os pixels** de cada conjunto de imagens
(referência vs lote) — não a distribuição de “imagens”, nem RGB canal a canal.
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

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("D (KS sobre L)", f"{payload['statistic']:.4f}")
m2.metric("valor-p", f"{payload['p_value']:.4g}")
m3.metric("n efectivo", f"{payload['n_eff']:.2f}")
m4.metric("n imagens referência", payload["n_images_corpus"])
m5.metric("n imagens lote", payload["n_images_production"])

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
A CDF acumula o histograma de **L** e divide pelo total de pixels: em cada
faixa, **F(L)** = fração dos pixels com luminância ≤ aquela faixa. Duas CDFs
iguais ⇒ mesma distribuição de L; o máximo de |F_ref − F_lote| é **D** do KS.
"""
)
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
Sobrepondo as curvas de **L**, o afastamento visual corresponde a **D**.
O banner resume **D** e o valor-p (ALERTA / ATENÇÃO / TRANQUILO / INCONCLUSIVO).
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

st.subheader("Mais miniaturas do lote")
thumbs = load_thumbnails(theme_paths_for_batch(batch_name))
if thumbs:
    st.image(thumbs, width=96)
else:
    st.info("Sem miniaturas para este nome de lote.")

with st.expander("Detalhe numérico do KS"):
    visivel = {
        k: v
        for k, v in payload.items()
        if not k.startswith("cdf") and not k.startswith("counts")
    }
    st.code(json.dumps(visivel, indent=2, ensure_ascii=False))
