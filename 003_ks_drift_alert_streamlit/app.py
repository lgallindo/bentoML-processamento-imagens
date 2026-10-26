"""Streamlit: KS corpus vs lote de production + banner + miniaturas."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import streamlit as st

from banner import banner_rule
from corpus_stats import load_default_corpus_stats
from ks_compare import compare_stats
from plotting import load_thumbnails, plot_dual_cdf
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


def list_batches() -> list[str]:
    if not BATCH_STATS_DIR.is_dir():
        return []
    return sorted(p.stem for p in BATCH_STATS_DIR.glob("*.json"))


def theme_paths_for_batch(name: str) -> list[Path]:
    """Heurística de miniaturas: nome do lote → samples/<tema>/."""
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


st.set_page_config(page_title="KS drift alert", layout="wide")
st.title("Alerta KS: corpus vs production")
st.caption(
    "Uma estatística de Kolmogorov–Smirnov sobre a CDF de L — "
    "parece magia negra quando o lote muda de tema."
)

batches = list_batches()
if not batches:
    st.warning(
        "Nenhum ficheiro em `batch_stats/`. "
        "Rode `just build-demo-batches` (offline) ou "
        "`just exercise-theme` + `just snapshot-batch` com o servidor no ar."
    )
    st.stop()

batch_name = st.sidebar.selectbox("Lote de production", batches)
bins = st.sidebar.slider("bins", min_value=16, max_value=256, value=256, step=16)

corpus = load_default_corpus_stats()
production = load_request_stats(BATCH_STATS_DIR / f"{batch_name}.json")
payload = compare_stats(corpus, production, channel="L", bins=bins)
state = banner_rule(
    payload["p_value"],
    payload["statistic"],
    payload["n_images_corpus"],
    payload["n_images_production"],
)

colors = {
    "ALERT": "#c62828",
    "WATCH": "#ef6c00",
    "QUIET": "#2e7d32",
    "INCONCLUSIVE": "#546e7a",
}
st.markdown(
    f"<div style='padding:1rem;border-radius:8px;background:{colors[state]};"
    f"color:white;font-size:1.4rem;font-weight:600'>{state}</div>",
    unsafe_allow_html=True,
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("D", f"{payload['statistic']:.4f}")
c2.metric("p-value", f"{payload['p_value']:.4g}")
c3.metric("n_eff", f"{payload['n_eff']:.2f}")
c4.metric("n corpus", payload["n_images_corpus"])
c5.metric("n production", payload["n_images_production"])

st.pyplot(
    plot_dual_cdf(
        payload["cdf_corpus"],
        payload["cdf_production"],
        title=f"CDF L — corpus vs {batch_name}",
    )
)

st.subheader("Miniaturas do lote (amostra)")
thumbs = load_thumbnails(theme_paths_for_batch(batch_name))
if thumbs:
    st.image(thumbs, width=96)
else:
    st.info("Sem miniaturas para este nome de lote.")

with st.expander("JSON do KS"):
    st.code(json.dumps({k: v for k, v in payload.items() if not k.startswith("cdf")}, indent=2))
