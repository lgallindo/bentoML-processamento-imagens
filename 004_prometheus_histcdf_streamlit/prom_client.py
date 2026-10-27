"""Cliente Prometheus: query instantânea e carga de fixture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

DEFAULT_PROM_URL = "http://127.0.0.1:9090"
DEFAULT_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "duration_histogram.json"
METRIC_BUCKET = "bentoml_service_request_duration_seconds_bucket"
INFERENCE_ENDPOINTS = ("/blur", "/grayscale", "/resize")


class PromClientError(RuntimeError):
    """Falha ao falar com o Prometheus ou ao interpretar a resposta."""


def _parse_le(raw: str) -> float:
    if raw in ("+Inf", "Inf", "+inf", "inf"):
        return float("inf")
    return float(raw)


def normalize_bucket_result(
    payload: dict[str, Any],
    *,
    endpoint: str | None = None,
) -> list[dict[str, Any]]:
    """Converte o JSON de ``/api/v1/query`` em amostras ``{le, value, labels}``."""
    if payload.get("status") != "success":
        raise PromClientError(f"resposta Prometheus sem success: {payload.get('status')!r}")
    data = payload.get("data") or {}
    result = data.get("result") or []
    samples: list[dict[str, Any]] = []
    for item in result:
        metric = dict(item.get("metric") or {})
        ep = metric.get("endpoint")
        if endpoint is not None and ep != endpoint:
            continue
        if "le" not in metric:
            continue
        value_pair = item.get("value")
        if not value_pair or len(value_pair) < 2:
            raise PromClientError("amostra sem value [ts, string]")
        samples.append(
            {
                "le": _parse_le(str(metric["le"])),
                "le_raw": str(metric["le"]),
                "value": float(value_pair[1]),
                "labels": metric,
            }
        )
    samples.sort(key=lambda s: (s["labels"].get("endpoint") or "", s["le"]))
    return samples


def aggregate_by_le(samples: list[dict[str, Any]]) -> list[tuple[float, float]]:
    """Soma contagens cumulativas por ``le`` (útil com vários endpoints)."""
    totals: dict[float, float] = {}
    for s in samples:
        totals[s["le"]] = totals.get(s["le"], 0.0) + float(s["value"])
    return sorted(totals.items(), key=lambda kv: kv[0])


def query_instant(
    expr: str,
    *,
    base_url: str = DEFAULT_PROM_URL,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """``GET {base}/api/v1/query?query=…`` — devolve o JSON bruto."""
    url = base_url.rstrip("/") + "/api/v1/query"
    try:
        resp = httpx.get(url, params={"query": expr}, timeout=timeout)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise PromClientError(f"Prometheus inacessível em {url}: {exc}") from exc
    try:
        payload = resp.json()
    except ValueError as exc:
        raise PromClientError("resposta Prometheus não é JSON") from exc
    if payload.get("status") != "success":
        raise PromClientError(f"query falhou: {payload.get('error') or payload}")
    return payload


def fetch_duration_buckets(
    *,
    base_url: str = DEFAULT_PROM_URL,
    endpoint: str | None = "/grayscale",
) -> list[dict[str, Any]]:
    """Busca buckets de duração; ``endpoint=None`` mantém blur|grayscale|resize."""
    if endpoint is None:
        filt = 'endpoint=~"/blur|/grayscale|/resize"'
    else:
        filt = f'endpoint="{endpoint}"'
    expr = f"{METRIC_BUCKET}{{{filt}}}"
    payload = query_instant(expr, base_url=base_url)
    samples = normalize_bucket_result(payload, endpoint=endpoint)
    if not samples:
        raise PromClientError("nenhuma amostra de bucket devolvida")
    return samples


def load_fixture(path: Path | None = None) -> dict[str, Any]:
    """Carrega JSON gravado de uma query bem-sucedida (sem rede)."""
    fixture_path = path or DEFAULT_FIXTURE
    try:
        text = fixture_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PromClientError(f"não foi possível ler fixture {fixture_path}: {exc}") from exc
    return json.loads(text)


def fetch_duration_buckets_from_fixture(
    path: Path | None = None,
    *,
    endpoint: str | None = "/grayscale",
) -> list[dict[str, Any]]:
    payload = load_fixture(path)
    samples = normalize_bucket_result(payload, endpoint=endpoint)
    if not samples:
        raise PromClientError("fixture sem amostras para o filtro pedido")
    return samples


def scalar_from_query(payload: dict[str, Any]) -> float | None:
    """Extrai um escalar (ou o primeiro valor de um vector) de uma query."""
    data = payload.get("data") or {}
    result_type = data.get("resultType")
    result = data.get("result")
    if result_type == "scalar" and isinstance(result, list) and len(result) >= 2:
        return float(result[1])
    if result_type == "vector" and result:
        value_pair = result[0].get("value")
        if value_pair and len(value_pair) >= 2:
            raw = value_pair[1]
            if raw in ("NaN", "+Inf", "-Inf"):
                return None
            return float(raw)
    return None
