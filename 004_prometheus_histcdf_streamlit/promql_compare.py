"""Constrói PromQL e empacota a comparação Python ↔ PromQL."""

from __future__ import annotations

from typing import Any

from prom_client import (
    DEFAULT_PROM_URL,
    METRIC_BUCKET,
    PromClientError,
    query_instant,
    scalar_from_query,
)
from prom_hist import histogram_quantile_from_cumulative, python_quantile_source


def build_histogram_quantile_promql(
    q: float,
    *,
    endpoint: str | None = "/grayscale",
) -> str:
    """Expressão instantânea (contadores cumulativos) para ``histogram_quantile``."""
    if endpoint is None:
        filt = 'endpoint=~"/blur|/grayscale|/resize"'
    else:
        filt = f'endpoint="{endpoint}"'
    return (
        f"histogram_quantile({q}, sum by (le) ({METRIC_BUCKET}{{{filt}}}))"
    )


def build_histogram_quantile_promql_rate(
    q: float,
    *,
    endpoint: str | None = "/grayscale",
    window: str = "1m",
) -> str:
    """Variante com ``rate`` (como a recording rule da raiz) — documentação."""
    if endpoint is None:
        filt = 'endpoint=~"/blur|/grayscale|/resize"'
    else:
        filt = f'endpoint="{endpoint}"'
    return (
        f"histogram_quantile({q}, sum by (le) "
        f"(rate({METRIC_BUCKET}{{{filt}}}[{window}])))"
    )


def compare_quantiles(
    les: list[float],
    cumulative: list[float],
    *,
    q: float = 0.95,
    endpoint: str | None = "/grayscale",
    promql_value: float | None = None,
    promql_available: bool = False,
) -> dict[str, Any]:
    """Payload de comparação: valores, delta e trechos de código."""
    py = histogram_quantile_from_cumulative(q, les, cumulative)
    promql = build_histogram_quantile_promql(q, endpoint=endpoint)
    py_val = py.get("value")
    delta_abs: float | None = None
    delta_rel: float | None = None
    if (
        promql_available
        and py_val is not None
        and promql_value is not None
        and promql_value == promql_value  # not NaN
    ):
        delta_abs = float(py_val) - float(promql_value)
        if promql_value != 0:
            delta_rel = delta_abs / abs(float(promql_value))

    return {
        "q": q,
        "python": py,
        "promql_expr": promql,
        "promql_expr_rate": build_histogram_quantile_promql_rate(q, endpoint=endpoint),
        "promql_value": promql_value if promql_available else None,
        "promql_available": promql_available,
        "delta_abs": delta_abs,
        "delta_rel": delta_rel,
        "python_source": python_quantile_source(),
    }


def fetch_promql_quantile(
    q: float,
    *,
    endpoint: str | None = "/grayscale",
    base_url: str = DEFAULT_PROM_URL,
) -> tuple[str, float | None]:
    """Executa a expressão instantânea; devolve ``(expr, valor_ou_None)``."""
    expr = build_histogram_quantile_promql(q, endpoint=endpoint)
    payload = query_instant(expr, base_url=base_url)
    return expr, scalar_from_query(payload)


def live_compare(
    les: list[float],
    cumulative: list[float],
    *,
    q: float = 0.95,
    endpoint: str | None = "/grayscale",
    base_url: str = DEFAULT_PROM_URL,
) -> dict[str, Any]:
    """Compara Python local com PromQL ao vivo; propaga erro de rede."""
    try:
        _expr, prom_val = fetch_promql_quantile(q, endpoint=endpoint, base_url=base_url)
        available = prom_val is not None
    except PromClientError:
        return compare_quantiles(
            les,
            cumulative,
            q=q,
            endpoint=endpoint,
            promql_value=None,
            promql_available=False,
        )
    return compare_quantiles(
        les,
        cumulative,
        q=q,
        endpoint=endpoint,
        promql_value=prom_val,
        promql_available=available,
    )
