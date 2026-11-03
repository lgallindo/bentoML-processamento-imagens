# Aula 016 — Dashboards Grafana sobre Prometheus

Depois de ler `/metrics` e PromQL na [`010`](../010_prometheus_promql/README.md)
(e, se quiser, o reforço Streamlit [`015`](../015_prometheus_histcdf_streamlit/README.md)),
fecha-se o caminho de **saúde** com painéis no Grafana — porta canónica
**4000**, nunca 3000.

O roteiro de instalação permanece em [`docs/grafana.md`](../docs/grafana.md).
Esta pasta é o handout numerado: objectivos, exercício e entrega.

## Objectivos

1. Ter Grafana em <http://127.0.0.1:4000> com a fonte Prometheus
   `127.0.0.1:9090` (provisionamento do repositório).
2. Montar (ou importar) um dashboard com: taxa por `endpoint`, **taxa de
   erro**, p95 de latência e linha de base (média ± k·σ).
3. Responder uma pergunta **só** com o gráfico — sem Streamlit.
4. Recordar o limite: o Grafana **consulta o Prometheus**, não o
   `/metrics` do BentoML directamente.

## Pré-requisitos

- Aula `010` concluída; BentoML em **3000**; Prometheus em **9090**.
- Tutorial [`docs/grafana.md`](../docs/grafana.md) (secções 1–3).
- Tráfego de exemplo (secção 4 do tutorial) ou o seu próprio exercitador.

## 1. Instale e provisione

Siga [`docs/grafana.md`](../docs/grafana.md): `http_port = 4000`, datasource
versionado em `monitoring/grafana/datasources/`. Confirme
`up{job="bentoml-imagens"} == 1` no Prometheus antes de abrir painéis.

## 2. Painéis exigidos

Use **Dashboards → New** (ou importe
[`monitoring/grafana/dashboards/bentoml-health.json`](../monitoring/grafana/dashboards/bentoml-health.json)
se o provisionamento de dashboards estiver activo).

| Painel | PromQL de partida (ajuste labels ao seu `/metrics`) |
| :--- | :--- |
| Requisições / s | `sum by (endpoint) (rate(bentoml_service_request_total[1m]))` |
| Taxa de erro | `sum by (endpoint) (rate(bentoml_service_request_total{http_response_code=~"5.."}[1m]))` — se o label diferir, use o nome real exposto em `/metrics` |
| p95 | `bentoml:http_request_duration_seconds:p95_1m` (recording rule) |
| Linha de base | p95 + `avg_over_time(...[30m]) + 3 * stddev_over_time(...[30m])` como no tutorial |

Detalhe passo a passo: secção «Monte o dashboard» em
[`docs/grafana.md`](../docs/grafana.md).

## 3. Exercício e entrega

1. Gere tráfego (tutorial §4) durante pelo menos um minuto.
2. Capture o dashboard (ou exporte JSON).
3. Responda por escrito, **citando só o gráfico**:
   «Neste intervalo, o p95 está / não está dentro do limite de três
   desvios-padrão? Em que `endpoint`?»
4. Não use o painel Streamlit da `015` para esta entrega.

## Critério de conclusão

- [ ] Painéis visíveis em `:4000`.
- [ ] Pergunta do §3 respondida com evidência do Grafana.
- [ ] Nenhuma URL de curso aponta Grafana em `:3000`.

## Roteiro da trilha

| | Pasta |
| :--- | :--- |
| **Anterior** | [`015_prometheus_histcdf_streamlit`](../015_prometheus_histcdf_streamlit/README.md) (ou `010` se saltar o reforço) |
| **Seguinte** | [`019_loki_grafana_logs`](../019_loki_grafana_logs/README.md) (logs OSS; se stub, avance ao Ato II [`011`](../011_corpus_histograms_model/README.md)) |
