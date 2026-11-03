# Aula 000 — Pipelines de MLOps e objetivos de monitoramento

Bem-vindo. Esta pasta abre a trilha: aqui você ganha o mapa — do
treinamento à inferência, e daí ao monitoramento — antes de entrar nos
detalhes de cada etapa.

O fio da história é um serviço de processamento de imagens. O
**Runtime (BentoML)** recebe pedidos do mundo, responde e publica métricas.
Observar esse serviço é o que liga todas as aulas. O caminho de
observabilidade é BentoML → Prometheus → Grafana; a instalação está nos
tutoriais de [Prometheus](../docs/prometheus.md) e
[Grafana](../docs/grafana.md).

## Portas locais padrão

Contrato do curso (detalhe em [`docs/ports.md`](../docs/ports.md)):

| Serviço | Porta |
| :--- | ---: |
| **BentoML** | **3000** |
| **Prometheus** | **9090** |
| **Grafana** | **4000** |

Painéis Streamlit das aulas: **8500 + N** (exemplo: `003` → `8503`;
`010` → `8510`).

## Objetivos finais de monitoramento

Três perguntas atravessam a trilha inteira:

1. Saúde do servidor — o serviço responde; taxa de erro e latência em faixa
   aceitável no caminho BentoML → Prometheus → Grafana.
2. Drift de dados — a distribuição dos pedidos (ou das features) se afasta do
   corpus de referência.
3. Detecção de anomalias — uma janela de métrica foge da linha de base (por
   exemplo média ± k desvios-padrão no p95).

## Visão de arquitetura

As figuras em [`illustrations/`](illustrations/) mostram o mesmo mapa em três
batidas. O diagrama resume as camadas:

```mermaid
flowchart LR
  W["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/mundo.png' width='56'/><br/>Mundo<br/>clientes / carga"]

  subgraph pipelines [Pipelines de MLOps]
    direction TB
    subgraph treino [Treinamento]
      direction LR
      DS["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/cientista.png' width='40'/><br/>Cientista / estatístico"]
      MD["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/modelo.png' width='48'/><br/>Modelo"]
      DS --> MD
    end
    subgraph infer [Inferência]
      direction LR
      B["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/bentoml.png' width='72'/><br/>BentoML<br/>empacota e serve"]
      R["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/oci.png' width='64'/><br/>Runtime (BentoML)<br/>contêiner"]
      B --> R
    end
    subgraph mon [Monitoramento]
      direction LR
      P["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/prometheus.png' width='48'/><br/>Prometheus<br/>papel: DB de séries"]
      G["<img src='https://raw.githubusercontent.com/lgallindo/bentoML-processamento-imagens/main/000_mlops_pipelines_goals/illustrations/logos/grafana.png' width='48'/><br/>Grafana<br/>papel: dashboard"]
      P --> G
    end
    MD --> B
    R -->|/metrics| P
  end

  W -.->|HTTP| R
```

Antes de medir saúde, é preciso ter o serviço no ar e expondo métricas. Os
tutoriais de Prometheus e Grafana cuidam disso na hora certa.

## Ordem de estudo em quatro atos

Estude nesta ordem. A numeração agrupa temas: `001`–`002` vocabulário;
`010`–`014` plataforma (saúde + tijolos); `003`–`006` teatro KS; `008` PSI.
A `003` e a `008` mantêm os paths estáveis (links e extratos Cloud).

**Ato 0 — Vocabulário.** Histograma e CDF, as duas leituras de distribuição
que sustentam o resto:
[`001_histogram_cdf_cli`](../001_histogram_cdf_cli/README.md) →
[`002_histogram_cdf_streamlit`](../002_histogram_cdf_streamlit/README.md).

**Ato I — Saúde do servidor.** Latência e séries no caminho BentoML →
Prometheus → Grafana:
[`010_prometheus_histcdf_streamlit`](../010_prometheus_histcdf_streamlit/README.md).

**Ato II — Tijolos no serviço.** Corpus, log e rotas de monitor — o caminho
dos dados; o juízo do alerta vem depois:
[`011_corpus_histograms_model`](../011_corpus_histograms_model/README.md) →
[`012_grayscale_request_logging`](../012_grayscale_request_logging/README.md) →
[`013_request_log_histograms`](../013_request_log_histograms/README.md) →
[`014_ks_production_vs_corpus`](../014_ks_production_vs_corpus/README.md).

**Ato III — Drift e anomalias.** O teatro das imagens: referência versus
lote, janela, entrada/saída, tráfego misto e, por fim, outro instrumento
(PSI):
[`003_ks_drift_alert_streamlit`](../003_ks_drift_alert_streamlit/README.md) →
[`004_ks_anomaly_detection_streamlit`](../004_ks_anomaly_detection_streamlit/README.md) →
[`005_ks_input_output_streamlit`](../005_ks_input_output_streamlit/README.md) →
[`006_ks_mixed_landscape_streamlit`](../006_ks_mixed_landscape_streamlit/README.md) →
[`008_psi_drift_alert_streamlit`](../008_psi_drift_alert_streamlit/README.md).

## Índice das aulas

Catálogo por pasta. Para **estudar**, use a ordem dos quatro atos acima.

### Ato 0 — Vocabulário

**[`001_histogram_cdf_cli`](../001_histogram_cdf_cli/README.md)** —
Aprende o que é um histograma (contagens por faixa) e uma CDF (fração
acumulada), com um microexemplo na linha de comando. Você produz JSON, CSV
ou PNG a partir de uma lista de números. É a base matemática de quase tudo
que vem depois — inclusive buckets de latência e luminância de imagens.

**[`002_histogram_cdf_streamlit`](../002_histogram_cdf_streamlit/README.md)** —
O mesmo objeto da `001`, agora num painel: cola valores (ou amostra), ajusta
bins e intervalo, vê tabela e gráfico juntos. Consolida a intuição antes de
falar de alertas ou Prometheus.

### Ato I — Saúde do servidor

**[`010_prometheus_histcdf_streamlit`](../010_prometheus_histcdf_streamlit/README.md)** —
Pergunta: a tubulação responde com latência interpretável? Você lê séries e
labels, distingue contador de taxa, reconstrói histograma/CDF a partir de
buckets do Prometheus, estima um p95 e redige um relato com limites. Não
mede qualidade de imagem nem drift de conteúdo — isso é o Ato III. Pré-req:
vocabulário `001`–`002` e o serviço/coleta dos tutoriais de Prometheus e
Grafana.

### Ato II — Tijolos no serviço

**[`011_corpus_histograms_model`](../011_corpus_histograms_model/README.md)** —
O serviço deixa de ser só filtro HTTP: entra um corpus de treino, um modelo
picklable de tons de cinza e rotas que reportam histogramas do corpus. Você
vê onde o «mundo de referência» mora no runtime.

**[`012_grayscale_request_logging`](../012_grayscale_request_logging/README.md)** —
Cada pedido a `/inference-grayscale` grava features em disco **antes** da
conversão para cinza (canais R/G/B ainda existem). Sem esse log, não há
*production* para comparar com o corpus.

**[`013_request_log_histograms`](../013_request_log_histograms/README.md)** —
Agrega o log e expõe histogramas de production ao lado dos do corpus, com
exercitador de carga. Serve para *olhar* o afastamento; o cartão de alerta
didático vem no Ato III.

**[`014_ks_production_vs_corpus`](../014_ks_production_vs_corpus/README.md)** —
Expõe no HTTP a estatística de Kolmogorov–Smirnov entre production e corpus
(D, valor-p, tamanhos efetivos). É o contrato de números no serviço — não
substitui o painel e o semáforo da `003`.

### Ato III — Drift e anomalias

**[`003_ks_drift_alert_streamlit`](../003_ks_drift_alert_streamlit/README.md)** —
Âncora do arco: HTTP pode estar verde e a latência aceitável, enquanto as
luminâncias dos pedidos já não parecem o treino. Fluxo L → histograma → CDF
→ D → alerta (com regra de amostra inconclusiva). Volta aqui depois dos
tijolos `011`–`014`.

**[`004_ks_anomaly_detection_streamlit`](../004_ks_anomaly_detection_streamlit/README.md)** —
Mesmo aparelho da `003`, outra escala: um candidato (uma imagem) ou uma
**janela** temporal de pedidos versus a referência. É o objetivo «detecção
de anomalias» em cena.

**[`005_ks_input_output_streamlit`](../005_ks_input_output_streamlit/README.md)** —
Dois alertas sobre D: luminância das imagens **submetidas** e das imagens
**devolvidas**. Mostra quando entrada e saída contam a mesma história — ou
quando o filtro as separa.

**[`006_ks_mixed_landscape_streamlit`](../006_ks_mixed_landscape_streamlit/README.md)** —
Tráfego misto (metade ainda «parece» treino, metade de outro mundo visual).
Pergunta: o alerta ainda dispara? Com que intensidade frente a controles
puros?

**[`008_psi_drift_alert_streamlit`](../008_psi_drift_alert_streamlit/README.md)** —
Irmã da `003`: mesma parábola operacional, outro instrumento (PSI e faixas
clássicas de monitoramento). Fecha o Ato III mostrando que trocar a métrica
não apaga a pergunta sobre o mundo dos dados.

---

Próximo passo:
[`001_histogram_cdf_cli`](../001_histogram_cdf_cli/README.md).
