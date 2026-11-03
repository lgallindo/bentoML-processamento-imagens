# Portas locais deste repositório

Mapa canônico para aulas e tutoriais. A abertura da trilha
([aula 000](../000_mlops_pipelines_goals/README.md)) reproduz o mesmo contrato.
Tutoriais: [Prometheus](prometheus.md), [Grafana](grafana.md).

## Trio canônico (observabilidade)

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
| 002 | 8502 | histograma+CDF |
| 003 | 8503 | alerta KS |
| 004 | 8504 | anomalia KS |
| 005 | 8505 | KS entrada/saída |
| 006 | 8506 | tráfego misto |
| 008 | 8508 | alerta PSI |
| 015 | 8515 | histograma/CDF Prometheus (após a 010) |

O painel Streamlit **não** substitui o BentoML em 3000.

## Demos sintéticas (opcionais)

Quando uma aula sobe exporter/Prometheus **além** do trio canônico:

| Papel | Regra |
| :--- | :--- |
| Exporter / fake `/metrics` | **8000 + N** |
| Prometheus só-demo | **9090 + N** |

Mapa por aula (N = número da pasta). Só use o par se essa aula de fato
subir a demo; o trio canônico **3000** / **9090** / **4000** continua válido
em paralelo e a demo **não** o substitui.

| Aula | Exporter (`8000+N`) | Prometheus demo (`9090+N`) |
| ---: | ---: | ---: |
| 001 | 8001 | 9091 |
| 002 | 8002 | 9092 |
| 003 | 8003 | 9093 |
| 004 | 8004 | 9094 |
| 005 | 8005 | 9095 |
| 006 | 8006 | 9096 |
| 008 | 8008 | 9098 |
| 010 | 8010 | 9100 |
| 011 | 8011 | 9101 |
| 012 | 8012 | 9102 |
| 013 | 8013 | 9103 |
| 014 | 8014 | 9104 |
| 015 | 8015 | 9105 |
