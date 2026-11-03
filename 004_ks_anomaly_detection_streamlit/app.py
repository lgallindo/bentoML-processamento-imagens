"""Painel Streamlit da aula 005: anomalia KS (candidato / janela vs ref).

Pré-condições:
  - corpus_stats.json carregável;
  - modo lote: batch_stats/*.json (via `just sync-demo-from-003`);
  - modo candidato: samples/<tema>/ na raiz do repositório Git.

Fluxo::

    modo candidato ──► score_path_vs_reference ──► alert_on_d(n=1) → INCONCLUSIVO
    modo lote ──► compare_stats ──► window_alert(n, D) → ALERTA|TRANQUILO|…

Saídas principais: UI Streamlit (sem API).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st
from PIL import Image

from alert_rule import ALERT_PT, alert_on_d
from anomaly import (
    DEFAULT_WINDOW_DAYS,
    D_ALERT,
    score_path_vs_reference,
    window_alert,
)
from corpus_stats import load_default_corpus_stats
from ks_compare import compare_stats
from plotting import plot_cdf_abs_diff, plot_dual_cdf, plot_histogram
from request_stats import load_request_stats

ROOT = Path(__file__).resolve().parent
BATCH_STATS_DIR = ROOT / "batch_stats"


def repo_root() -> Path:
    return Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )


st.set_page_config(page_title="Anomalia KS", layout="wide")
st.title("Anomalia KS — candidato vs referência")

st.header("Meta desta aula")
st.markdown(
    """
A aula **003** compara **dois lotes** (treino vs produção) e alerta sobre
**D**. Aqui o mesmo aparelho (L → histograma → CDF → δ → **D**) serve a
**detecção de anomalia**:

1. **Uma imagem candidata** contra a referência de treino, ou
2. Uma **janela temporal** de pedidos recentes (time boxing, ex.: últimos
   30 dias) agregada e comparada à mesma referência.

Reutilizamos definições e limiar \(D \\ge 0{,}10\). Sem lote mínimo na janela,
o estado é **INCONCLUSIVO** — uma foto isolada move **D**, mas não fecha o
alarme operacional.
"""
)

st.header("Definições (iguais à 003)")
st.markdown(
    r"""
- **L** — cinza do pixel \(0\ldots255\) após `convert("L")`.
- **Histograma** — contagens \(h_k\); **CDF** \(F_k=(1/N)\sum_{i\le k}h_i\).
- **D** — \(\max_k|F^{\mathrm{ref}}_k - F^{\mathrm{cand}}_k|\).
- **Time boxing** — só entram no lote de monitoramento imagens cujo instante
  cai na janela (ex.: 30 dias). Em produção isso evita misturar anos de log.
"""
)

referencia = load_default_corpus_stats()
ref_counts = referencia["histograms"]["luminance"]["counts"]

with st.sidebar:
    st.header("Modo")
    modo = st.radio(
        "Comparação",
        ("Uma imagem candidata", "Lote em batch_stats (janela didática)"),
    )
    n_intervalos = st.slider("Faixas de L", 16, 256, 256, 16)
    st.caption(f"Limiar de alerta: D ≥ {D_ALERT:.2f}")
    st.caption(f"Janela típica de produção: {DEFAULT_WINDOW_DAYS} dias")

if modo.startswith("Uma imagem"):
    st.header("Candidato único")
    samples = repo_root() / "samples"
    tema = st.selectbox("Pasta de amostras", ["balls", "forests", "beaches"])
    tema_dir = samples / tema
    if not tema_dir.is_dir():
        raise FileNotFoundError(
            f"amostras ausentes: {tema_dir} "
            "(confirme samples/<tema>/ na raiz do repositório)"
        )
    paths = sorted(tema_dir.glob("*.jpg"))
    if not paths:
        raise FileNotFoundError(
            f"nenhum JPG em {tema_dir} "
            "(confirme samples/<tema>/ na raiz do repositório)"
        )
    escolha = st.selectbox("Arquivo", paths, format_func=lambda p: p.name)
    payload = score_path_vs_reference(escolha, ref_counts, bins=n_intervalos)
    # Uma imagem: n=1 → INCONCLUSIVO na regra operacional
    estado = alert_on_d(payload["statistic"], n_images=1)
    st.markdown(
        f"<div style='padding:1rem;border-radius:8px;background:"
        f"{'#c62828' if estado=='ALERT' else '#546e7a' if estado=='INCONCLUSIVE' else '#2e7d32'};"
        f"color:white;font-size:1.3rem;font-weight:600'>"
        f"{ALERT_PT[estado]} — D = {payload['statistic']:.4f}</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Com **uma** imagem o alerta operacional é INCONCLUSIVO (time boxing / "
        "mínimo de pedidos na janela). **D** ainda diagnostica o afastamento."
    )
    st.image(Image.open(escolha), caption=escolha.name, width=280)
    c1, c2 = st.columns(2)
    with c1:
        st.pyplot(
            plot_histogram(
                payload["counts_reference"],
                title="Histograma L — referência",
                series_label="treino",
                color="#1565c0",
            )
        )
    with c2:
        st.pyplot(
            plot_histogram(
                payload["counts_candidate"],
                title="Histograma L — candidato",
                series_label=escolha.name,
                color="#ef6c00",
            )
        )
    st.pyplot(
        plot_dual_cdf(
            payload["cdf_reference"],
            payload["cdf_candidate"],
            title="CDFs — referência vs candidato",
            label_referencia="referência",
            label_lote="candidato",
        )
    )
    st.pyplot(
        plot_cdf_abs_diff(
            payload["cdf_reference"],
            payload["cdf_candidate"],
            title="δ e D",
        )
    )
else:
    st.header("Lote vs referência (reuso dos batch_stats)")
    st.markdown(
        """
Na sala usamos `batch_stats/*.json` como **proxy** de uma janela temporal
já agregada. Em produção, a janela seriam os pedidos dos últimos N dias.
"""
    )
    if not BATCH_STATS_DIR.is_dir():
        raise FileNotFoundError(
            f"batch_stats ausente: {BATCH_STATS_DIR} "
            "(rode `just sync-demo-from-003` ou `just build-demo-batches` na 003)"
        )
    batches = sorted(p.stem for p in BATCH_STATS_DIR.glob("*.json"))
    if not batches:
        raise FileNotFoundError(
            f"nenhum JSON em {BATCH_STATS_DIR} "
            "(rode `just sync-demo-from-003` ou `just build-demo-batches` na 003)"
        )
    nome = st.selectbox("Lote", batches)
    lote = load_request_stats(BATCH_STATS_DIR / f"{nome}.json")
    cmp = compare_stats(referencia, lote, channel="L", bins=n_intervalos)
    estado = window_alert(cmp["n_images_production"], cmp["statistic"])
    cores = {"ALERT": "#c62828", "QUIET": "#2e7d32", "INCONCLUSIVE": "#546e7a"}
    st.markdown(
        f"<div style='padding:1rem;border-radius:8px;background:{cores[estado]};"
        f"color:white;font-size:1.3rem;font-weight:600'>"
        f"{ALERT_PT[estado]} — D = {cmp['statistic']:.4f} "
        f"(n lote = {cmp['n_images_production']})</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Regra: INCONCLUSIVO se n &lt; 8 na janela; ALERTA se D ≥ 0,10; "
        "senão TRANQUILO. Valor-p calculado mas fora da regra de alerta."
    )
    st.pyplot(
        plot_dual_cdf(
            cmp["cdf_corpus"],
            cmp["cdf_production"],
            title=f"CDFs — referência vs {nome}",
            label_referencia="referência",
            label_lote=nome,
        )
    )
    st.pyplot(plot_cdf_abs_diff(cmp["cdf_corpus"], cmp["cdf_production"]))
    with st.expander("JSON"):
        st.code(
            json.dumps(
                {k: v for k, v in cmp.items() if not k.startswith(("cdf", "counts"))},
                indent=2,
            )
        )
