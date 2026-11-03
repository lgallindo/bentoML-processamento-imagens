# Portas locais deste repositório

Mapa canónico para aulas e tutoriais. A abertura da trilha
([aula 000](../000_mlops_pipelines_goals/README.md)) reproduz o mesmo contrato.
Tutoriais: [Prometheus](prometheus.md), [Grafana](grafana.md).

## Trio canónico (observabilidade)

| Serviço | Porta | URL local | Como sobe |
| :--- | ---: | :--- | :--- |
| **BentoML** (API + `GET /metrics`) | **3000** | <http://127.0.0.1:3000> | `just serve` na raiz |
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
| 002 | 8502 | `just app` / painel histograma+CDF |
| 003 | 8503 | `just streamlit` |
| 004 | 8504 | `just app` (PromQL / histograma de latência) |
| 005 | 8505 | … |
| 006 | 8506 | … |
| 007 | 8507 | … |
| 008 | 8508 | … |

O painel Streamlit **não** substitui o BentoML em 3000.

## Demos sintéticas (opcionais)

Quando uma aula sobe exporter/Prometheus **além** do trio canónico:

| Papel | Regra | Exemplo (aula 004) |
| :--- | :--- | :--- |
| Exporter / fake `/metrics` | **8000 + N** | 8004 |
| Prometheus só-demo | **9090 + N** (N &lt; 10) | 9094 |

O canónico 3000 / 9090 / 4000 continua válido em paralelo; a demo não o
substitui.
