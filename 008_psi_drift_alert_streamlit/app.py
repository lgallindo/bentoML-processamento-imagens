"""Streamlit: PSI da luminância (média por imagem + espelho por pixel)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st
from PIL import Image

from alert_psi import alert_on_psi, label_pt
from corpus_stats import load_default_corpus_stats
from ks_compare import compare_stats
from plotting import (
    load_thumbnails,
    plot_histogram,
    plot_mass_bars,
    plot_means_hist,
)
from psi import MEAN_BINS_DEFAULT, compare_psi_means, compare_psi_pixels
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"

CORES = {
    "ALERT": "#c62828",
    "WATCH": "#ef6c00",
    "QUIET": "#2e7d32",
    "INCONCLUSIVE": "#546e7a",
}

ALGORITMO_PSI = """\
# Variáveis:
# p_ref[b], p_lote[b] — massas relativas na faixa b (soma = 1)
# eps — suavização se massa zero (ex.: 1e-6)
# PSI, b, pr, pl

PSI ← 0
para cada b:
    pr ← max(p_ref[b], eps)
    pl ← max(p_lote[b], eps)
    PSI ← PSI + (pl − pr) · ln(pl / pr)
"""

POC_L = '''from PIL import Image

img = Image.open("foto.jpg").convert("L")  # L ∈ {0, …, 255} por pixel
media_L = sum(img.getdata()) / (img.width * img.height)
'''

LOTE_ROTULO = {
    "control": "Mesmo tema (outro trecho de praias)",
    "forests": "Florestas",
    "beaches": "Praias",
    "balls": "Bolas",
    "landscapes": "Mistura praias e florestas",
}


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


st.set_page_config(page_title="Alerta PSI de drift", layout="wide")
st.title("Alerta PSI de drift")

st.header("Meta desta aula")
st.markdown(
    """
Este serviço pode responder **rápido** e com **HTTP 200** e, mesmo assim,
trabalhar sobre um mundo diferente do treino. A latência mede espera. Ela
não mede se os **dados** ainda combinam com a referência.

Aqui você resume o afastamento entre referência e lote no
**Population Stability Index (PSI)** e lê faixas clássicas de monitoramento
de scorecards: estável, investigar, mudança forte.
"""
)

st.header("Definições")

st.subheader("L — luminância")
st.markdown(
    r"""
Uma fotografia digital é uma grade de **pixels**. Em cores, cada pixel
costuma carregar três canais. Para falar de “quão claro ou escuro” é o
ponto, convertemos a imagem para tons de cinza com `Image.convert("L")`:
cada pixel vira um inteiro \(L \in \{0,1,\ldots,255\}\).

Nesta aula o PSI trabalha em **duas escalas**:

- **P2 (alerta principal)** — uma observação por imagem: a **média de L**
  da foto. As faixas vêm dos quantis da referência (ex.: 10 faixas).
- **P1 (espelho)** — histograma de L **por pixel**, no mesmo espírito da
  aula KS, para comparar o número com o que você já viu em \(D\).
"""
)
st.code(POC_L, language="python")

st.subheader("PSI")
st.markdown(
    r"""
Nas mesmas \(K\) faixas, \(p_{\mathrm{ref}}[b]\) e \(p_{\mathrm{lote}}[b]\)
são as **massas relativas** (frações que somam 1). O índice é

$$
\mathrm{PSI}
= \sum_b
\bigl(p_{\mathrm{lote}}[b] - p_{\mathrm{ref}}[b]\bigr)
\cdot
\ln\frac{p_{\mathrm{lote}}[b]}{p_{\mathrm{ref}}[b]},
$$

com suavização \(\varepsilon\) (ex.: \(10^{-6}\)) quando alguma massa é
zero: usa-se \(\max(p,\varepsilon)\) dentro do logaritmo.
"""
)
st.code(ALGORITMO_PSI, language="text")

st.subheader("Faixas de alerta")
st.markdown(
    r"""
Cortes clássicos de *credit scoring* / monitoramento de scorecards
(Siddiqi e material de ongoing monitoring):

| Estado | Condição | Leitura |
| :--- | :--- | :--- |
| INCONCLUSIVO | \(n &lt; 8\) em qualquer lado | Janela / lote ainda fino |
| ESTÁVEL | \(n \ge 8\) e PSI &lt; 0,10 | Compatível com a referência |
| INVESTIGAR | \(n \ge 8\) e 0,10 ≤ PSI ≤ 0,25 | Mudança moderada |
| MUDANÇA FORTE | \(n \ge 8\) e PSI &gt; 0,25 | Afastamento forte |

Em produção o lote é uma **caixa de tempo** (por exemplo pedidos dos
últimos 30 dias). Os JSON em `batch_stats/` fazem o papel de uma janela
já agregada.
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
    n_mean_bins = st.slider(
        "Faixas P2 (média de L por imagem)",
        min_value=5,
        max_value=20,
        value=MEAN_BINS_DEFAULT,
        step=1,
    )
    n_pixel_bins = st.slider(
        "Faixas P1 (histograma de L por pixel)",
        min_value=16,
        max_value=256,
        value=256,
        step=16,
    )
    mostrar_ks = st.checkbox("Mostrar D (KS) ao lado, só para comparação", value=True)

referencia = load_default_corpus_stats()
lote = load_request_stats(BATCH_STATS_DIR / f"{batch_name}.json")
p2 = compare_psi_means(referencia, lote, n_bins=n_mean_bins)
p1 = compare_psi_pixels(referencia, lote, channel="L", bins=n_pixel_bins)
estado_p2 = alert_on_psi(
    p2["psi"], p2["n_images_corpus"], p2["n_images_production"]
)
estado_p1 = alert_on_psi(
    p1["psi"], p1["n_images_corpus"], p1["n_images_production"]
)

label_ref = "referência (praias de treino)"
label_lote = rotulo_lote(batch_name)
amostra_ref = caminhos_referencia()[:1]
amostra_lote = theme_paths_for_batch(batch_name)[:1]

st.header("Alerta principal — PSI P2 (média de L por imagem)")
st.markdown(
    f"<div style='padding:1rem;border-radius:8px;background:{CORES[estado_p2]};"
    f"color:white;font-size:1.4rem;font-weight:600'>"
    f"{label_pt(estado_p2)} — PSI (P2) = {p2['psi']:.4f}</div>",
    unsafe_allow_html=True,
)
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("PSI P2 (média de L)", f"{p2['psi']:.4f}")
col_m2.metric("Imagens na referência", p2["n_images_corpus"])
col_m3.metric("Imagens no lote", p2["n_images_production"])

st.header("1. Distribuição das médias de L (P2)")
col_a, col_b = st.columns(2)
with col_a:
    mostrar_amostra(
        amostra_ref[0] if amostra_ref else None,
        "Amostra da referência",
    )
with col_b:
    mostrar_amostra(
        amostra_lote[0] if amostra_lote else None,
        "Amostra do lote",
    )
st.pyplot(
    plot_means_hist(
        p2["means_ref"],
        p2["means_lote"],
        p2["edges"],
        title="Médias de L por imagem — mesmas faixas (quantis da referência)",
        label_ref=label_ref,
        label_lote=label_lote,
    )
)
st.pyplot(
    plot_mass_bars(
        p2["p_ref"],
        p2["p_lote"],
        title="Massas relativas por faixa (P2)",
        label_ref=label_ref,
        label_lote=label_lote,
        xlabel="faixa (quantil da referência)",
    )
)

st.header("2. Espelho P1 — PSI no histograma de L por pixel")
st.markdown(
    f"<div style='padding:0.75rem;border-radius:8px;background:{CORES[estado_p1]};"
    f"color:white;font-size:1.1rem;font-weight:600'>"
    f"{label_pt(estado_p1)} — PSI (P1) = {p1['psi']:.4f}</div>",
    unsafe_allow_html=True,
)
st.caption(
    "P1 usa a mesma grade de L dos pixels da aula KS. "
    "O alerta **operacional** desta lição é o P2; P1 existe para você "
    "comparar a sensibilidade das duas variáveis."
)
col_h1, col_h2 = st.columns(2)
with col_h1:
    st.pyplot(
        plot_histogram(
            p1["counts_ref"],
            title="Histograma de L (pixels) — referência",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with col_h2:
    st.pyplot(
        plot_histogram(
            p1["counts_lote"],
            title="Histograma de L (pixels) — lote",
            series_label=label_lote,
            color="#ef6c00",
        )
    )

if mostrar_ks:
    ks = compare_stats(referencia, lote, channel="L", bins=n_pixel_bins)
    st.header("3. Comparação opcional com D (KS)")
    st.metric("D (Kolmogorov–Smirnov sobre L por pixel)", f"{ks['statistic']:.4f}")
    st.caption(
        "O KS resume o máximo afastamento entre CDFs. O PSI soma uma "
        "contribuição por faixa das massas. São histórias diferentes do "
        "mesmo histograma de pixels."
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
    detalhe = {
        "p2": {
            k: v
            for k, v in p2.items()
            if k
            not in {
                "means_ref",
                "means_lote",
                "p_ref",
                "p_lote",
                "counts_ref",
                "counts_lote",
            }
        },
        "p1": {
            k: v
            for k, v in p1.items()
            if k not in {"p_ref", "p_lote", "counts_ref", "counts_lote"}
        },
        "alerta_p2": label_pt(estado_p2),
        "alerta_p1": label_pt(estado_p1),
    }
    st.code(json.dumps(detalhe, indent=2, ensure_ascii=False))
