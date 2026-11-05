# Demo auxiliar — exporter 8010 + Prometheus 9100

[Voltar à aula 021](README.md).

Esta demo é a **mesma** da
[`010_prometheus_promql/SAMPLE_DATA.md`](../010_prometheus_promql/SAMPLE_DATA.md):
gerador sintético em **8010**, Prometheus dedicado em **9100**, regras de
[`monitoring/bentoml.rules.yml`](../monitoring/bentoml.rules.yml). Use-a
quando `:9090` no Host não for o Prometheus do curso (sem job
`bentoml-imagens`).

As portas **8010** / **9100** são auxiliares. O contrato do curso para o
serviço real continua BentoML **3000** e Prometheus **9090**
([`docs/ports.md`](../docs/ports.md)).

## Subir a demo

Terminal 1 (a partir da pasta da 010, onde está o gerador):

```bash
cd ../010_prometheus_promql
just demo-exporter
```

Terminal 2:

```bash
cd ../010_prometheus_promql
just demo-prometheus
```

Confirme <http://127.0.0.1:9100/targets> (`bentoml-imagens` UP) e abra
<http://127.0.0.1:9100/alerts>.

Durante a fase lenta do gerador (ver tabela de fases na SAMPLE_DATA da 010),
acompanhe pending. Com a regra 3σ e pouca história no TSDB, o pending pode
aparecer no primeiro salto de latência; cumprir `for: 1m` até firing é
frágil no ciclo de 6 min (o limiar adapta-se). As figuras da aula documentam
esse contrato.

## Consulta de apoio

```promql
ALERTS{alertname="BentoMLResponseTimeAnomaly"}
```
