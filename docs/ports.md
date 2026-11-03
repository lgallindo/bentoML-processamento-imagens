# Portas locais deste repositório

Mapa canónico para aulas e tutoriais. A abertura da trilha
([aula 000](../000_mlops_pipelines_goals/README.md)) reproduz o mesmo contrato.
Tutoriais: [Prometheus](prometheus.md), [Grafana](grafana.md).
Handouts: [009 OCI](../009_bentoml_oci_runtime/README.md),
[016 Grafana](../016_grafana_dashboards/README.md).

## Trio canónico (observabilidade)

| Serviço | Porta | URL local | Como sobe |
| :--- | ---: | :--- | :--- |
| **BentoML** (API + `GET /metrics`) | **3000** | <http://127.0.0.1:3000> | `just serve` na raiz (ou `just oci-smoke` na 009) |
| **Prometheus** (UI + API; scrape do BentoML) | **9090** | <http://127.0.0.1:9090> | binário + `monitoring/prometheus.yml` |
| **Grafana** (dashboards) | **4000** | <http://127.0.0.1:4000> | ver [grafana.md](grafana.md) (`http_port = 4000`) |

```text
cliente → BentoML :3000/metrics ← Prometheus :9090 ← Grafana :4000
```

**Invariantes:** Grafana **não** usa a porta 3000 neste projeto (o default
upstream do Grafana colide com o BentoML). A UI do Prometheus permanece em
9090. Não documente Grafana@3000 como padrão do curso.

## Painéis Streamlit (por aula)

Pasta `NNN_*` → porta **8500 + N** (N = número da aula).

| Aula | Porta | Exemplo |
| ---: | ---: | :--- |
| 002 | 8502 | histograma+CDF |
| 003 | 8503 | alerta KS |
| 004 | 8504 | anomalia KS |
| 005 | 8505 | KS entrada/saída |
| 006 | 8506 | tráfego misto |
| 008 | 8508 | alerta PSI |
| 015 | 8515 | histograma/CDF Prometheus (após a 010) |

A aula **010** (`010_prometheus_promql`) não usa Streamlit.

O painel Streamlit **não** substitui o BentoML em 3000.

## Aulas sem Streamlit (inventário)

| Aula | Porta(s) | Notas |
| ---: | :--- | :--- |
| 009 | 3000 | OCI/runtime; sem painel Streamlit |
| 016 | 4000 | UI Grafana (handout; ver grafana.md) |
| 017 | 8125 / 8126 | Datadog agent (auxiliar; omitir se sem lab) |
| 018 | 9200 | Elasticsearch (auxiliar; eixo logs; stub) |
| 019 | 3100 | Loki (auxiliar; Explore no Grafana 4000; handout completo) |
| 020 | — | contrato de monitoramento (sem serviço) |

## Demos sintéticas (opcionais)

Quando uma aula sobe exporter/Prometheus **além** do trio canónico:

| Papel | Regra | Exemplo (aula 010) |
| :--- | :--- | :--- |
| Exporter / fake `/metrics` | **8000 + N** | 8010 |
| Prometheus só-demo | **9090 + N** | 9100 |

O canónico 3000 / 9090 / 4000 continua válido em paralelo; a demo não o
substitui.
