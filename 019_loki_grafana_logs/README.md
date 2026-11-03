# Aula 019 — Loki + Grafana (logs OSS) — em construção

Handout previsto: Promtail (ou Alloy) → Loki → Explore no Grafana
**4000**, correlacionando um pico de latência (Prometheus) com linhas de log.

## Estado

Stub da trilha. Pré-req planeado:
[`016_grafana_dashboards`](../016_grafana_dashboards/README.md) + fonte de log
(`012` ou stdout do BentoML).

## Notas de desenho

- Porta auxiliar típica Loki **3100** — registar em
  [`docs/ports.md`](../docs/ports.md) na PR do handout.
- LogQL básico: `{job="bentoml"} |= "inference"`.
- Exercício: correlacionar Prom ↔ Loki na mesma janela temporal.
- Se a `016` ainda não estiver feita no ambiente do aluno, o pré-req pode
  apontar a [`docs/grafana.md`](../docs/grafana.md).

## Roteiro

| | Pasta |
| :--- | :--- |
| **Anterior** | [`016_grafana_dashboards`](../016_grafana_dashboards/README.md) |
| **Seguinte** | [`018_elasticsearch_logs`](../018_elasticsearch_logs/README.md) (ou Ato II se for stub) |
