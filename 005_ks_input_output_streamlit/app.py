"""Streamlit: KS na entrada e KS na saída (alerta sobre D em cada lado)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st
from PIL import Image

from alert_rule import alert_on_d
from corpus_stats import load_corpus_stats
from ks_compare import compare_stats
from plotting import load_thumbnails, plot_dual_cdf, plot_histogram
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"

ALERTA_PT = {
    "ALERT": "ALERTA",
    "QUIET": "TRANQUILO",
    "INCONCLUSIVE": "INCONCLUSIVO",
}

CORES = {
    "ALERT": "#c62828",
    "QUIET": "#2e7d32",
    "INCONCLUSIVE": "#546e7a",
}

LOTES = ("control", "forests")
LOTE_ROTULO = {
    "control": "Mesmo tema (outro trecho de praias)",
    "forests": "Florestas",
}


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


def caminhos_tema(tema: str, offset: int = 0, count: int = 8) -> list[Path]:
    folder = repo_root() / "samples" / tema
    paths = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg"))
    return paths[offset : offset + count]


def alert_html(titulo: str, estado: str, d: float) -> str:
    return (
        f"<div style='padding:1rem;border-radius:8px;background:{CORES[estado]};"
        f"color:white;font-size:1.15rem;font-weight:600'>"
        f"{titulo}<br/>{ALERTA_PT[estado]} — D = {d:.4f}</div>"
    )


def leitura_conjunta(est_in: str, est_out: str) -> str:
    if est_in == "QUIET" and est_out == "QUIET":
        return (
            "Entrada e saída estão **TRANQUILO**: o tráfego e o que o serviço "
            "emite ainda combinam com a referência de treino nesta métrica."
        )
    if est_in == "ALERT" and est_out == "ALERT":
        return (
            "Entrada e saída em **ALERTA**: os pedidos mudaram e a emissão "
            "acompanha — o filtro está **espelhando** o drift de uso."
        )
    if est_in == "QUIET" and est_out == "ALERT":
        return (
            "Entrada **TRANQUILO** e saída **ALERTA**: os pedidos parecem o "
            "treino, mas o que o serviço devolve divergiu. Investigue o "
            "caminho de inferência (modelo trocado, pré-processamento, bug)."
        )
    if est_in == "ALERT" and est_out == "QUIET":
        return (
            "Entrada **ALERTA** e saída **TRANQUILO**: combinação improvável "
            "neste filtro de cinza; revise se os JSONs de lote batem com o "
            "modo escolhido."
        )
    return (
        "Pelo menos um lado está **INCONCLUSIVO** (poucas imagens na "
        "comparação). Espere mais pedidos na janela antes de fechar o alarme."
    )


st.set_page_config(page_title="KS entrada × saída", layout="wide")
st.title("KS na entrada e na saída")

st.header("Meta desta aula")
st.markdown(
    """
Um serviço pode estar **saudável em HTTP** e mesmo assim trabalhar sobre um
mundo diferente do treino. A [aula 003](../003_ks_drift_alert_streamlit/README.md)
mede isso na luminância **L** das imagens **submetidas**.

Aqui a pergunta se desdobra. O cliente manda uma imagem — **entrada**. O
serviço devolve outra — **saída**. Cada lado tem a sua distribuição de L,
a sua CDF, o seu **D**, o seu alerta.

Quando entrada e saída contam a mesma história, o filtro está espelhando o
uso. Quando a entrada parece estável e a saída não, algo no caminho de
inferência mudou.
"""
)

st.header("Definições")
st.markdown(
    r"""
**L** é o tom de cinza do pixel após `Image.convert("L")` — 0 preto, 255
branco. O **histograma** conta pixels por faixa; a **CDF** acumula a
fração até cada faixa; \(\delta_k = \lvert F_k - G_k \rvert\) e
\(D = \max_k \delta_k\).

A regra de alerta é a mesma da 003: **INCONCLUSIVO** se \(n &lt; 8\) em
qualquer lado; **ALERTA** se \(D \ge 0{,}10\); senão **TRANQUILO**. O
valor-p assintótico pode aparecer como nota; **não** move o alarme.

No modo **saudável**, a saída é só `convert("L")` — entrada e saída tendem
a contar a mesma história. No modo **deslocado**, a saída soma +40 em cada
pixel de L (com teto 255): com o lote de controle, a entrada fica
TRANQUILO e a saída dispara ALERTA — o contraste operacional da aula.
"""
)

with st.sidebar:
    st.header("Parâmetros")
    lote_nome = st.selectbox(
        "Lote",
        LOTES,
        format_func=lambda n: LOTE_ROTULO[n],
    )
    modo = st.radio(
        "Modo de saída",
        ("saudável", "deslocado"),
        help=(
            "Deslocado compara a saída alterada (+40 em L) com a referência "
            "de emissão saudável do treino."
        ),
    )
    n_intervalos = st.slider(
        "Número de faixas do histograma de L",
        min_value=16,
        max_value=256,
        value=256,
        step=16,
    )

ref_in = load_corpus_stats(ROOT / "corpus_stats_input.json")
ref_out = load_corpus_stats(ROOT / "corpus_stats_output.json")
lote_in = load_request_stats(BATCH_STATS_DIR / f"{lote_nome}_input.json")
if modo == "saudável":
    lote_out_path = BATCH_STATS_DIR / f"{lote_nome}_output.json"
else:
    lote_out_path = BATCH_STATS_DIR / f"{lote_nome}_output_shifted.json"
    if not lote_out_path.is_file():
        st.error(
            f"Não há `{lote_out_path.name}` para este lote. "
            "O freeze offline só materializa saída deslocada para **control**. "
            "Escolha control ou rode o exercício shifted no servidor."
        )
        st.stop()

lote_out = load_request_stats(lote_out_path)

payload_in = compare_stats(ref_in, lote_in, channel="L", bins=n_intervalos)
payload_out = compare_stats(ref_out, lote_out, channel="L", bins=n_intervalos)
estado_in = alert_on_d(
    payload_in["statistic"],
    payload_in["n_images_corpus"],
    payload_in["n_images_production"],
)
estado_out = alert_on_d(
    payload_out["statistic"],
    payload_out["n_images_corpus"],
    payload_out["n_images_production"],
)

st.header("Alertas lado a lado")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        alert_html("Entrada (pedidos)", estado_in, payload_in["statistic"]),
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        alert_html(
            f"Saída ({modo})",
            estado_out,
            payload_out["statistic"],
        ),
        unsafe_allow_html=True,
    )

st.markdown(leitura_conjunta(estado_in, estado_out))
st.caption(
    f"Notas: valor-p entrada ≈ {payload_in['p_value']:.4g}; "
    f"valor-p saída ≈ {payload_out['p_value']:.4g}. "
    "O alerta responde só a D."
)

label_ref = "referência (praias de treino)"
label_lote = LOTE_ROTULO[lote_nome]

st.header("1. Histogramas de L — entrada")
c1, c2 = st.columns(2)
with c1:
    st.pyplot(
        plot_histogram(
            payload_in["counts_corpus"],
            title="Entrada — referência",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with c2:
    st.pyplot(
        plot_histogram(
            payload_in["counts_production"],
            title="Entrada — lote",
            series_label=label_lote,
            color="#ef6c00",
        )
    )

st.header("2. Histogramas de L — saída")
c3, c4 = st.columns(2)
with c3:
    st.pyplot(
        plot_histogram(
            payload_out["counts_corpus"],
            title="Saída — referência (emissão saudável do treino)",
            series_label=label_ref,
            color="#1565c0",
        )
    )
with c4:
    st.pyplot(
        plot_histogram(
            payload_out["counts_production"],
            title=f"Saída — lote ({modo})",
            series_label=label_lote,
            color="#6a1b9a",
        )
    )

st.header("3. CDFs — entrada e saída")
d1, d2 = st.columns(2)
with d1:
    st.pyplot(
        plot_dual_cdf(
            payload_in["cdf_corpus"],
            payload_in["cdf_production"],
            title="CDF entrada — referência e lote",
            label_referencia=label_ref,
            label_lote=label_lote,
        )
    )
with d2:
    st.pyplot(
        plot_dual_cdf(
            payload_out["cdf_corpus"],
            payload_out["cdf_production"],
            title=f"CDF saída ({modo}) — referência e lote",
            label_referencia=label_ref,
            label_lote=label_lote,
        )
    )

st.header("Miniaturas")
tema_lote = "beaches" if lote_nome == "control" else "forests"
off = 50 if lote_nome == "control" else 0
box1, box2 = st.columns(2)
with box1:
    with st.container(border=True):
        st.markdown("**Entrada (amostras do lote)**")
        thumbs = load_thumbnails(caminhos_tema(tema_lote, offset=off, count=8))
        if thumbs:
            st.image(thumbs, width=96)
with box2:
    with st.container(border=True):
        st.markdown("**Saída (cinza da 1ª amostra)**")
        amostra = caminhos_tema(tema_lote, offset=off, count=1)
        if amostra:
            img = Image.open(amostra[0]).convert("L")
            if modo == "deslocado":
                img = img.point(lambda p: min(255, p + 40))
            st.image(img, caption=amostra[0].name, width=220)

with st.expander("Detalhe numérico"):

    def slim(payload: dict) -> dict:
        return {
            k: v
            for k, v in payload.items()
            if not k.startswith("cdf") and not k.startswith("counts")
        }

    st.code(
        json.dumps(
            {"entrada": slim(payload_in), "saida": slim(payload_out)},
            indent=2,
            ensure_ascii=False,
        )
    )
