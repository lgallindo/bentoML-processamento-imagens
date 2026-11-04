# Aula 020 — Contrato de monitoramento (fecho)

**Conceito desta aula:** fechar a trilha redigindo **uma página** que amarra
os três fins de monitoramento — saúde do servidor, drift de dados, detecção
de anomalias — a **sinal**, **limiar**, **acção** e **dono**. As aulas
`NNN_*` entram aqui só como **proveniência** dos sinais que você já praticou;
esta pasta não sobe serviço novo.

Use o modelo [`CONTRACT_TEMPLATE.md`](CONTRACT_TEMPLATE.md).

## Filosofia DevOps

Um sistema operável é aquele em que alguém sabe, quando um número cruza uma
linha, o que fazer a seguir. Uma demonstração funciona enquanto o autor está
presente. Um serviço funciona quando a resposta a «o que fazemos agora?»
está escrita. O contrato de monitoramento guarda essa resposta em quatro
campos: **sinal** (o que se mede), **limiar** (a partir de quando está
errado), **acção** (o passo concreto) e **dono** (quem executa).

Cinco hábitos que o texto precisa carregar:

1. Um sinal só é útil quando alguém o interpreta no contexto deste serviço
   BentoML de imagens.
2. Um limiar indica **quando agir**, não apenas que «algo mudou».
3. Toda acção nomeia um responsável identificável e um próximo passo
   executável.
4. Se o alerta não muda uma decisão, reveja o sinal ou retire o alerta do
   contrato.
5. Depois de agir, anote o resultado; ajuste o contrato quando a evidência
   mostrar que ele falhou.

O campo **dono** é o que mais falha na prática: limiar sem dono vira aviso
que todos veem e ninguém atende. Escreva um nome ou um papel real. Mantenha
o contrato no repositório, ao lado do código — quem assume o serviço lê o
mesmo texto, e cada mudança de limiar deixa commit com data e motivo.

Admitir lacunas faz parte do contrato. Se um lab ficou de fora (chave SaaS
ausente, disco insuficiente para um harness), escreva «não disponível» —
não invente cobertura. Uma linha honesta informa mais do que um limiar
falso.

## Objetivos de MLOps nesta trilha

O fio condutor é o **Runtime** BentoML de processamento de imagens: o mundo
envia pedidos HTTP; o serviço responde; o monitoramento pergunta se a
máquina, os dados e o comportamento ainda merecem confiança. Os três fins
anunciados em
[`000_mlops_pipelines_goals`](../000_mlops_pipelines_goals/README.md)
viram três perguntas que o contrato **responde com uma linha cada**:

1. **Saúde do servidor** — o serviço responde; taxa de erro e latência
   (p95, alertas) estão em faixa aceitável?
2. **Drift de dados** — a distribuição dos pedidos (ou das features) se
   afastou do corpus de referência?
3. **Detecção de anomalias** — uma janela ou um candidato foge da linha de
   base a ponto de merecer inspeção?

Cada pergunta pede: sinal + fonte (`NNN_*`) + limiar (número e janela) +
acção + dono. «Muito alto» e «anormal» não bastam — o dono ficaria sem
critério.

## Por que fechar com um contrato

Um gráfico mostra o valor de um sinal. Não registra por que o limiar está
onde está, quem responde quando ele é cruzado, nem o que se faz depois. A
tabela em Markdown carrega o que o gráfico omite: cabe em diff, em revisão
e no clone do repositório.

## Portas que esta aula espera no Host

Nenhuma — só o editor e o modelo Markdown. Esta aula **não** sobe Container,
Scrape nem Dashboard; ela **cita** sinais cuja proveniência está nas pastas
da trilha.

## A trilha como proveniência de sinais

Cada aula anterior é uma **fonte** possível no campo «Fonte» do modelo.
Você **não** precisa reabrir as UIs agora: escolha sinais que você de fato
observou. Preferir um sinal visto a inventar um limiar elegância.

| Aula | O que pratica | Sinal tipicamente citável | Encaixa em |
| :--- | :--- | :--- | :--- |
| `000_mlops_pipelines_goals` | Mapa dos três fins | — (rótulos dos objetivos) | Vocabulário |
| `001_histogram_cdf_cli` | Histograma e CDF na CLI | Contagens / CDF de uma amostra | Vocabulário |
| `002_histogram_cdf_streamlit` | Histograma e CDF interativos | Mesma geometria, com controles | Vocabulário |
| `009_bentoml_oci_runtime` | Bento + imagem OCI; `/metrics` no Container | Famílias expostas em `GET /metrics` | Empacotamento |
| `010_prometheus_promql` | Scrape, PromQL, `rate`, p95, alertas | `up`, taxa por Endpoint, p95, estado `firing`/`pending` | Saúde |
| `015_prometheus_histcdf_streamlit` | Histograma/CDF sobre buckets | Distribuição de latência alinhada aos buckets | Saúde |
| `016_grafana_dashboards` | Dashboard de saúde | Painéis de taxa, erro, p95 / linha de base | Saúde |
| `019_loki_grafana_logs` | LogQL + Explore | Contagem de linhas `phase=slow` / erro na janela | Saúde (eixo logs) |
| `018_elasticsearch_logs` | `_bulk` / `_search` | Hits por `phase` ou filtro de latência | Saúde (eixo documentos) |
| `017_datadog_apm_metrics` | Labels ↔ tags; lab OpenMetrics opcional | Métrica SaaS com tags equivalentes (só se RUN) | Saúde (vendor) |
| `011_corpus_histograms_model` | Corpus e histograma de referência | Baseline de L (ou canais) no corpus | Tijolo |
| `012_grayscale_request_logging` | Log por pedido grayscale | JSON em `request_features/` | Tijolo |
| `013_request_log_histograms` | Histogramas do log | Histograma de production agregado | Tijolo |
| `014_ks_production_vs_corpus` | KS no serviço | `statistic` / `p_value` production vs corpus | Drift |
| `003_ks_drift_alert_streamlit` | Alerta KS (teatro) | \(D\) ≥ limiar no lote | Drift |
| `004_ks_anomaly_detection_streamlit` | Candidato / janela vs referência | Alerta ou INCONCLUSIVO por \(n\) | Anomalia |
| `005_ks_input_output_streamlit` | KS entrada e saída | Par de \(D\) (in / out) | Drift |
| `006_ks_mixed_landscape_streamlit` | Tráfego misto | \(D\) no lote landscapes vs controles | Drift |
| `008_psi_drift_alert_streamlit` | Alerta PSI | PSI e faixa (estável / mudança / forte) | Drift |

**Como escolher.** Um sinal por fim. Pastas de vocabulário ou tijolo
sustentam a medição; o contrato de alerta precisa de um sinal de **Saúde**,
**Drift** ou **Anomalia**. Se `017` ficou SKIP, não cite Datadog como fonte —
use a seção de lacunas com «não disponível».

## Como proceder

1. Abra [`CONTRACT_TEMPLATE.md`](CONTRACT_TEMPLATE.md) (copie para um arquivo
   local se quiser versionar a sua versão fora do Git do curso).
2. Preencha as três tabelas (saúde, drift, anomalia): sinal, fonte (`NNN_*`),
   limiar, acção, dono.
3. Na seção de lacunas, declare o que ficou de fora e o impacto no contrato.
4. Releia os cinco hábitos da filosofia DevOps: cada linha do contrato deve
   sobreviver a essa lista.

### Exemplo de linha (saúde)

| Campo | Exemplo |
| :--- | :--- |
| Sinal | p95 de `bentoml_service_request_duration_seconds` no job da aula |
| Fonte | `010_prometheus_promql` (e/ou painel em `016_grafana_dashboards`) |
| Limiar | p95 acima de média + 3σ por ≥ 1 min (regra do repositório) |
| Acção | Investigar Endpoint lento; reduzir carga; checar Container |
| Dono | Papel «plantão do serviço» (nomeie uma pessoa na sua turma/lab) |

### Exemplo de linha (drift)

| Campo | Exemplo |
| :--- | :--- |
| Sinal | Estatística \(D\) (KS) lote vs referência |
| Fonte | `003_ks_drift_alert_streamlit` ou `014_ks_production_vs_corpus` |
| Limiar | \(D \ge 0{,}10\) com \(n\) mínimo da aula |
| Acção | Congelar promoção do lote; inspecionar tema das imagens |
| Dono | Papel «dados / qualidade de entrada» |

## Conclusão (autoavaliação)

Marque **Sim** ou **Não** sozinho.

| Verificação | Sim / Não |
| :--- | :---: |
| As três tabelas têm sinal + limiar + acção + dono | |
| Cada sinal aponta a uma pasta `NNN_*` que você de fato praticou (ou lacuna explícita) | |
| Limiares são numéricos (ou faixas nomeadas da aula, ex. PSI) com janela quando couber | |
| Lacunas conscientes estão escritas sem inventar cobertura | |
| O texto passa nos cinco hábitos DevOps desta aula | |

## Roteiro

| | Pasta |
| :--- | :--- |
| **Anterior** | [`008_psi_drift_alert_streamlit`](../008_psi_drift_alert_streamlit/README.md) |
| **Seguinte** | — |
