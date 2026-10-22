"""App Streamlit: histograma e CDF a partir de uma lista de números."""

from __future__ import annotations

import io

import numpy as np
import pandas as pd
import streamlit as st

from histcdf import DEFAULT_BINS, histogram_with_cdf
from plotting import plot_histogram_cdf


def parse_values(text: str) -> np.ndarray:
    parts: list[float] = []
    for chunk in text.replace(";", ",").replace("\n", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            parts.append(float(chunk))
    return np.asarray(parts, dtype=float)


def sample_uniform(n: int = 200, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(0.0, 10.0, size=n)


def sample_normal(n: int = 200, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=5.0, scale=1.5, size=n)


st.set_page_config(page_title="Histograma e CDF", layout="wide")
st.title("Histograma e CDF")
st.caption("Lista de números → contagens por bin → CDF em [0, 1].")

with st.sidebar:
    st.header("Parâmetros")
    bins = st.slider("bins", min_value=1, max_value=50, value=DEFAULT_BINS)
    use_range = st.checkbox("Fixar intervalo [lo, hi]", value=False)
    lo = st.number_input("lo", value=0.0, disabled=not use_range)
    hi = st.number_input("hi", value=10.0, disabled=not use_range)
    st.divider()
    if st.button("Amostra uniforme"):
        st.session_state.values_text = ",".join(f"{x:.4f}" for x in sample_uniform())
    if st.button("Amostra normal"):
        st.session_state.values_text = ",".join(f"{x:.4f}" for x in sample_normal())

if "values_text" not in st.session_state:
    st.session_state.values_text = "1, 2, 2, 5"

upload = st.file_uploader("CSV com uma coluna numérica (opcional)", type=["csv"])
text = st.text_area("Valores (vírgula ou linha)", key="values_text", height=120)

try:
    if upload is not None:
        raw = upload.read().decode("utf-8")
        # primeira coluna numérica
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        col0 = []
        for ln in lines:
            cell = ln.split(",")[0].strip()
            if cell.lower() in {"value", "values", "x", "n"}:
                continue
            col0.append(float(cell))
        values = np.asarray(col0, dtype=float)
    else:
        values = parse_values(text)

    value_range = (float(lo), float(hi)) if use_range else None
    payload = histogram_with_cdf(values, bins=bins, value_range=value_range)
except Exception as exc:  # noqa: BLE001 — mostrar erro amigável na UI
    st.error(str(exc))
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("n", payload["n"])
c2.metric("mín", f"{values.min():.4g}")
c3.metric("máx", f"{values.max():.4g}")

fig = plot_histogram_cdf(payload["counts"], payload["edges"], payload["cdf"])

buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=120)
st.pyplot(fig, clear_figure=True)

rows = []
edges = payload["edges"]
for i, (count, cdf) in enumerate(zip(payload["counts"], payload["cdf"], strict=True)):
    rows.append(
        {
            "bin": i,
            "left": edges[i],
            "right": edges[i + 1],
            "count": count,
            "cdf": cdf,
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True)
st.download_button("Baixar PNG", data=buf.getvalue(), file_name="histogram_cdf.png")
