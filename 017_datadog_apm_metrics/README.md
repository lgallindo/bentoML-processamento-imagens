# Aula 017 — Datadog (métricas / APM) — em construção

Handout previsto: observar o **mesmo** serviço BentoML por um vendor SaaS
(métricas e/ou APM), contrastando com o Prometheus local — sem substituir o
trio canónico 3000 / 9090 / 4000.

## Estado

Stub da trilha. Pré-req planeado: [`010_prometheus_promql`](../010_prometheus_promql/README.md).
Ordem de estudo após Grafana/logs OSS: ver
[`000_mlops_pipelines_goals`](../000_mlops_pipelines_goals/README.md).

## Notas de desenho (quando houver key de lab)

- API key **apenas** em `.env` local (nunca no Git).
- **DEGRADE-001:** omitir ou deixar a key em branco → saltar o laboratório
  SaaS; as aulas `010`/`016` continuam válidas.
- Portas auxiliares do agent (ex. 8125 / 8126): documentar em
  [`docs/ports.md`](../docs/ports.md) na PR do handout completo.
- Exercício previsto: captura do dashboard Datadog + parágrafo «o que o
  Prometheus local ainda faz melhor nesta trilha».

## Roteiro

| | Pasta |
| :--- | :--- |
| **Anterior** | [`018_elasticsearch_logs`](../018_elasticsearch_logs/README.md) |
| **Seguinte** | Ato II — [`011_corpus_histograms_model`](../011_corpus_histograms_model/README.md) |
