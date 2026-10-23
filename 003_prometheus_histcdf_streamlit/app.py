"""App Streamlit: buckets Prometheus → tabela, histograma, CDF, Python ↔ PromQL."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from plotting import plot_histogram_cdf
from prom_client import (
    DEFAULT_PROM_URL,
    PromClientError,
    fetch_duration_buckets,
    fetch_duration_buckets_from_fixture,
)
from prom_hist import payload_from_samples
from promql_compare import compare_quantiles, live_compare

st.set_page_config(page_title="Prometheus histograma e CDF", layout="wide")
st.title("Histograma e CDF a partir do Prometheus")
st.caption(
    "Buckets cumulativos de "
    "`bentoml_service_request_duration_seconds` → tabela, gráfico e "
    "comparação Python ↔ PromQL (forma instantânea)."
)

with st.sidebar:
    st.header("Fonte")
    mode = st.radio("Modo", ("fixture", "live"), index=0)
    base_url = st.text_input("Prometheus URL", value=DEFAULT_PROM_URL)
    endpoint_label = st.selectbox(
        "Endpoint",
        options=["/grayscale", "/blur", "/resize", "(todos blur|grayscale|resize)"],
        index=0,
    )
    endpoint: str | None
    if endpoint_label.startswith("("):
        endpoint = None
    else:
        endpoint = endpoint_label
    q = st.select_slider("Quantil", options=[0.5, 0.9, 0.95, 0.99], value=0.95)
    refresh = st.button("Atualizar", type="primary")

if "loaded" not in st.session_state or refresh:
    st.session_state.loaded = True
    st.session_state.error = None
    st.session_state.samples = None
    st.session_state.payload = None
    st.session_state.compare = None
    try:
        if mode == "fixture":
            samples = fetch_duration_buckets_from_fixture(endpoint=endpoint)
            payload = payload_from_samples(samples)
            compare = compare_quantiles(
                payload["les"],
                payload["cumulative"],
                q=float(q),
                endpoint=endpoint,
                promql_value=None,
                promql_available=False,
            )
        else:
            samples = fetch_duration_buckets(base_url=base_url, endpoint=endpoint)
            payload = payload_from_samples(samples)
            compare = live_compare(
                payload["les"],
                payload["cumulative"],
                q=float(q),
                endpoint=endpoint,
                base_url=base_url,
            )
        st.session_state.samples = samples
        st.session_state.payload = payload
        st.session_state.compare = compare
    except (PromClientError, ValueError) as exc:
        st.session_state.error = str(exc)

if st.session_state.error:
    st.error(st.session_state.error)
    st.stop()

payload = st.session_state.payload
compare = st.session_state.compare
if payload is None or compare is None:
    st.info("Clique em Atualizar na barra lateral.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("total (cumulativo)", f"{payload['total']:.0f}")
c2.metric("bins finitos", f"{len(payload['counts'])}")
py_val = compare["python"].get("value")
c3.metric(f"Python p{int(q * 100)}", f"{py_val:.6f} s" if py_val is not None else "—")

rows = []
for le, cum, pb, lo, hi in zip(
    payload["les"],
    payload["cumulative"],
    payload["per_bin"],
    payload["lowers"],
    payload["uppers"],
    strict=True,
):
    rows.append(
        {
            "le": "+Inf" if le == float("inf") else le,
            "lower": lo,
            "upper": "+Inf" if hi == float("inf") else hi,
            "cumulative": cum,
            "per_bin": pb,
        }
    )
# CDF alinhada aos bins finitos
finite_rows = [r for r in rows if r["le"] != "+Inf"]
for i, cdf_v in enumerate(payload["cdf"]):
    if i < len(finite_rows):
        finite_rows[i]["cdf"] = cdf_v
for r in rows:
    if "cdf" not in r:
        r["cdf"] = None

st.subheader("Tabela de buckets")
st.dataframe(pd.DataFrame(rows), use_container_width=True)

if payload["cdf"]:
    st.subheader("Gráfico")
    fig = plot_histogram_cdf(payload["counts"], payload["edges"], payload["cdf"])
    st.pyplot(fig)
else:
    st.warning("Massa nula nos bins finitos — sem CDF para plotar.")

st.subheader("Comparação numérica (Python ↔ PromQL)")
prom_val = compare.get("promql_value")
delta = compare.get("delta_abs")
comp_df = pd.DataFrame(
    [
        {
            "lado": "Python",
            "valor_s": py_val,
            "nota": "walk + interpolação linear no bin",
        },
        {
            "lado": "PromQL",
            "valor_s": prom_val if compare["promql_available"] else None,
            "nota": (
                "histogram_quantile (instantâneo)"
                if compare["promql_available"]
                else "indisponível neste modo / query"
            ),
        },
        {
            "lado": "Δ (Python − PromQL)",
            "valor_s": delta,
            "nota": (
                f"rel={compare['delta_rel']:.4f}"
                if compare.get("delta_rel") is not None
                else "—"
            ),
        },
    ]
)
st.dataframe(comp_df, use_container_width=True)
if mode == "fixture":
    st.caption(
        "Modo fixture: o valor PromQL não é consultado. Em live, a mesma "
        "expressão abaixo é enviada a `/api/v1/query`."
    )

st.subheader("Complexidade: código Python vs PromQL")
col_py, col_prom = st.columns(2)
with col_py:
    st.markdown("**Python** (`histogram_quantile_from_cumulative`)")
    st.code(compare["python_source"], language="python")
with col_prom:
    st.markdown("**PromQL** (forma instantânea — a que o app usa)")
    st.code(compare["promql_expr"], language="text")
    st.markdown("**PromQL** (variante com `rate`, como a recording rule da raiz)")
    st.code(compare["promql_expr_rate"], language="text")
