# Aula 018 — Elasticsearch (logs de pedido) — em construção

Handout previsto: indexar **logs de pedido** (JSON da aula `012` ou fixture)
no Elasticsearch e consultar com Dev Tools / Kibana — eixo **logs**, não
reimplementar métricas Prometheus.

## Estado

Stub da trilha. Pré-req planeado:
[`012_grayscale_request_logging`](../012_grayscale_request_logging/README.md)
(ou fixture mínima nesta pasta).

## Notas de desenho

- Porta auxiliar típica **9200** — registar em [`docs/ports.md`](../docs/ports.md)
  antes do handout completo.
- Baby step: `curl` bulk de N linhas; Docker opcional (espaço no volume de
  pesquisa).
- Contraste explícito: ES ≠ Prometheus (eventos vs séries).
- Não misturar APM Datadog nesta pasta.

## Roteiro

| | Pasta |
| :--- | :--- |
| **Anterior** | [`019_loki_grafana_logs`](../019_loki_grafana_logs/README.md) |
| **Seguinte** | [`017_datadog_apm_metrics`](../017_datadog_apm_metrics/README.md) |
