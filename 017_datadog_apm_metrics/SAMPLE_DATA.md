# Dados e modo SKIP desta aula

Esta pasta **não** sobe Datadog Agent nem Contêiner extra no modo padrão.
O contrato de portas do curso (BentoML **3000**, Prometheus **9090**, Grafana
**4000**) permanece; o Agent, quando houver chave, raspa o mesmo
`http://127.0.0.1:3000/metrics` em paralelo.

## Sem chave (SKIP) — artefatos locais

| Arquivo | Uso |
| :--- | :--- |
| [`fixtures/sample_metrics_snippet.txt`](fixtures/sample_metrics_snippet.txt) | Trecho OpenMetrics didático (mesmo dialeto do curso) |
| [`fixtures/label_tag_pairs.example.json`](fixtures/label_tag_pairs.example.json) | Três pares label→tag de referência |
| [`fixtures/gate_skip.example.txt`](fixtures/gate_skip.example.txt) | Saída esperada de `check_datadog_gate.py` sem chave |
| [`monitoring/openmetrics.example.yaml`](monitoring/openmetrics.example.yaml) | Check OpenMetrics completo para copiar ao Agent no lab |

~~~bash
cd 017_datadog_apm_metrics
python3 scripts/check_datadog_gate.py
python3 scripts/map_labels_from_fixture.py
~~~

Não é obrigatório ter BentoML à escuta: o mapa de labels lê o fixture.

## Com chave (RUN)

Portas auxiliares do Agent: **8125** (DogStatsD), **8126** (APM) — ver
[`docs/ports.md`](../docs/ports.md). Copie o YAML de exemplo para a conf. do
Agent **fora** do Git; nunca versione `DD_API_KEY`.
