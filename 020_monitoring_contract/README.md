# Aula 020 — Contrato de monitoramento

**Conceito desta aula:** concluir a trilha preenchendo **uma página** que
amarra os três fins de monitoramento da
[`000_mlops_pipelines_goals`](../000_mlops_pipelines_goals/README.md) —
**saúde do servidor**, **drift de dados**, **detecção de anomalias** — a
quatro campos: **sinal**, **limiar**, **ação** e **dono**. Esta pasta não
sobe serviço novo e não pede Dashboard nem Scrape; você cita sinais que já
praticou nas aulas anteriores.

## O que quebra sem dono

Na aula de PromQL, o p95 do Endpoint de grayscale dispara (`firing`) enquanto
o HTTP continua 200: a imagem sai, o cliente não vê erro, e o painel de
sucesso permanece verde. No mesmo curso, um lote de paisagens em KS ou PSI
cruza o limiar de drift frente ao corpus — o serviço ainda converte; só o
mundo de entrada mudou.

Se o limiar existe sem **ação** e sem **dono**, os dois eventos viram o mesmo
aviso órfão: alguém vê o número, ninguém decide o próximo passo, e o pipeline
segue "saudável" na superfície. O contrato existe para impedir esse vazio —
uma linha por fim, com responsável nomeado.

## Quatro campos

| Campo | Pergunta que responde | Eco na bibliografia |
| :--- | :--- | :--- |
| **Sinal** | O que se mede, com nome de série ou estatística? | Página de sintoma (B1): o que o operador vê primeiro |
| **Limiar** | A partir de qual valor e janela isso está errado? | Alerta acionável (B6, B9): quando agir, não "algo mudou" |
| **Ação** | Qual o próximo passo concreto se o limiar for cruzado? | Mesma linha: o alerta muda uma decisão |
| **Dono** | Quem executa essa ação (pessoa ou papel real)? | Filosofia de alerta (B9): alguém atende; "a equipe" não atende |

Cada fim da trilha (saúde, drift, anomalia) recebe **uma** linha com esses
quatro campos.

## Filosofia DevOps

Um sistema operável é aquele em que alguém sabe, quando um número cruza uma
linha, o que fazer a seguir. Uma demonstração funciona enquanto o autor está
presente. Um serviço funciona quando a resposta a "o que fazemos agora?"
está escrita.

Cinco hábitos que o texto precisa carregar:

1. Um sinal só é útil quando alguém o interpreta no contexto deste serviço
   BentoML de imagens.
2. Um limiar indica **quando agir**, não apenas que "algo mudou".
3. Toda ação nomeia um responsável identificável e um próximo passo
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
ausente, disco insuficiente para um harness), escreva "não disponível" —
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
ação + dono. "Muito alto" e "anormal" não bastam — o dono ficaria sem
critério.

## O que a tabela guarda e o gráfico não

Um gráfico mostra o valor de um sinal. Não registra por que o limiar está
onde está, quem responde quando ele é cruzado, nem o que se faz depois. A
tabela em Markdown carrega o que o gráfico omite: cabe em diff, em revisão
e no clone do repositório.

## Campos *Ops* — de onde vêm os rótulos

Desde o fim dos anos 2000 a indústria anexou o sufixo **Ops** a quase toda
especialidade que precisa entregar e manter um artefato em produção. Os
cinco rótulos abaixo **não** formam uma escada oficial; sobrepõem-se. Os
quatro campos desta aula (sinal / limiar / ação / dono) são a gramática
comum; *Ops* nomeia **quem** costuma falar cada idioma.

| Rótulo | Objeto típico | Pergunta-mãe |
| :--- | :--- | :--- |
| **DevOps** | Serviço (código + infra) | O pipeline responde e se libera com segurança? |
| **MLOps** | Modelo + dados + serving | O comportamento aprendido ainda merece confiança? |
| **CVOps** | Pipeline de visão | O mundo visual mudou (anotação, GPU, drift de pixels)? |
| **LLMOps** | Produto com modelo de linguagem | Prompt, contexto, custo e qualidade ainda cabem no contrato? |
| **AIOps** | Telemetria da operação de TI | Dá para correlacionar e priorizar o dilúvio de alertas? |

### DevOps (c. 2007–2009 → )

Patrick Debois e Andrew Shafer discutem *Agile Infrastructure* (2008). Em
2009, no O’Reilly Velocity, John Allspaw e Paul Hammond (Flickr) apresentam
["10+ Deploys Per Day"](https://www.youtube.com/watch?v=LdOe18KhtT4);
Debois organiza o primeiro
[devopsdays](https://devopsdays.org/)
em Ghent. Relatos:
[Origins of DevOps](https://devops.com/the-origins-of-devops-whats-in-a-name/),
[Convergence of DevOps](https://itrevolution.com/articles/the-convergence-of-devops/).
Não é um produto: é liberar software com frequência, com observação e
dono compartilhado. Nesta trilha = **saúde do pipeline**
([`003`](../003_ks_drift_alert_streamlit/README.md) / [`008`](../008_psi_drift_alert_streamlit/README.md)
§ DevOps;
[`010`](../010_prometheus_promql/README.md),
[`016`](../016_grafana_dashboards/README.md)).

### MLOps (débito técnico 2015 → termo c. 2017–2018 → )

Sculley et al.,
["Hidden Technical Debt in Machine Learning Systems"](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf)
(NeurIPS 2015), descrevem o custo fora do retângulo do "modelo". O léxico
**MLOps** espalha-se depois; síntese:
[Kreuzberger et al., IEEE Access 2023](https://ieeexplore.ieee.org/document/10069172),
[NVIDIA — MLOps](https://www.nvidia.com/en-us/glossary/mlops/).
O paper de 2015 descreve a dívida; **não** batiza o campo
([Last Dictionary](https://lastdictionary.com/mlops)).
Nesta trilha = título da
[`000`](../000_mlops_pipelines_goals/README.md)
e os fins **drift** / **anomalia**
([`003`](../003_ks_drift_alert_streamlit/README.md)–[`006`](../006_ks_mixed_landscape_streamlit/README.md),
[`008`](../008_psi_drift_alert_streamlit/README.md),
[`004`](../004_ks_anomaly_detection_streamlit/README.md),
[`011`](../011_corpus_histograms_model/README.md)–[`014`](../014_ks_production_vs_corpus/README.md)).

### CVOps (final dos anos 2010 → )

Rótulo de mercado para "MLOps quando o dado é imagem/vídeo": arquivos
grandes, anotação, GPU, drift visual —
[Picsellia](https://www.picsellia.com/post/how-to-apply-mlops-to-computer-vision-cvops),
[Xailient](https://xailient.com/blog/xailient-created-cvops-for-edge-computer-vision-at-scale/).
Este curso **é** laboratório de visão (grayscale, L, beaches/forests), mas
o handout quase não escreve "CVOps": o conteúdo fica sob MLOps + DevOps.

### LLMOps (c. 2022–2024 → )

Operação de produtos com modelos de linguagem (prompt, contexto, custo,
avaliação) —
[NVIDIA — LLMOps](https://developer.nvidia.com/blog/mastering-llm-techniques-llmops/).
**Fora de escopo** desta trilha: não há pasta `NNN_*` de prompt/RAG/LLM.

### AIOps (Gartner, 2017 → )

Plataformas de *algorithmic IT operations* sobre telemetria de TI —
[comunicado Gartner (2017-04-11)](https://www.gartner.com/en/newsroom/press-releases/2017-04-11-gartner-says-algorithmic-it-operations-drives-digital-business);
contraste com MLOps:
[Opensource.com](https://opensource.com/article/21/2/aiops-vs-mlops).
Nesta trilha há só **eco** didático (aula
[`004`](../004_ks_anomaly_detection_streamlit/README.md),
alertas Prometheus): não há correlacionador multi-fonte nem plataforma
AIOps.

### Como o contrato corta o mapa

| Linha do contrato | Eco *Ops* | Fonte típica |
| :--- | :--- | :--- |
| Saúde | DevOps (+ SRE/Prometheus) | `010`, `021`, `022` |
| Drift | MLOps (CVOps implícito) | `003`, `008`, `014` |
| Anomalia | MLOps; eco fraco de AIOps | `004` |
| Lacunas | Honestidade operacional | lab SKIP, sinal não visto |

A parábola do p95 `firing` com HTTP 200 e do lote KS/PSI com serviço ainda
convertendo é a fronteira DevOps × MLOps/CVOps.

## Escopo Negativo

| Isto **não** é o contrato | Por quê |
| :--- | :--- |
| Montar ou polir um Dashboard | Dashboard mostra séries; não registra dono nem ação |
| Colar o dump de `GET /metrics` | O texto cru lista famílias; o contrato escolhe **um** sinal por fim |
| Preencher formulário sem sinal praticado | Inventar limiar elegante sem ter visto o gráfico ou o painel |
| Subir Container, Prometheus ou Grafana nesta pasta | Exercício textual; Scrape e Dashboard ficam nas aulas que os operam |
| Recitar os cinco hábitos sem aplicá-los a cada linha | Os hábitos servem para revisar o artefato; o critério é o preenchimento |
| Memorizar a cronologia *Ops* | História contextualiza; o critério Sim/Não é o artefato |

## Como proceder

Escreva **três linhas** (caderno, arquivo local ou o editor que preferir) —
uma por fim — com sinal, limiar, ação e dono. A fonte deve ser uma pasta
`NNN_*` que você de fato praticou. Fontes típicas (não é inventário
completo):

- Saúde: `010_prometheus_promql` (p95, `up`, taxa); `022_prometheus_rules_ui`
  (`/rules`); `021_prometheus_alerts_ui` (`/alerts`)
- Drift: `003_ks_drift_alert_streamlit` ou `008_psi_drift_alert_streamlit`
- Anomalia: `004_ks_anomaly_detection_streamlit`

Declare também as **lacunas**: o que ficou de fora (lab SKIP, sinal não
observado) e o impacto — escreva "não disponível"; não invente cobertura.
Não há formulário separado nesta pasta; os exemplos abaixo bastam como
modelo. Releia os cinco hábitos da Filosofia DevOps: cada linha deve
sobreviver a essa lista.

### Exemplo trabalhado (saúde)

| Campo | Exemplo |
| :--- | :--- |
| Sinal | p95 de `bentoml_service_request_duration_seconds` no job da aula |
| Fonte | `010_prometheus_promql` |
| Limiar | p95 acima da linha de base da regra do repositório por pelo menos 1 min |
| Ação | Investigar Endpoint lento; reduzir carga; checar Container |
| Dono | Papel "plantão do serviço" (nomeie uma pessoa da turma ou do lab) |

### Exemplo trabalhado (drift)

| Campo | Exemplo |
| :--- | :--- |
| Sinal | Estatística D (KS) do lote frente à referência — ou PSI na faixa da aula |
| Fonte | `003_ks_drift_alert_streamlit` ou `008_psi_drift_alert_streamlit` |
| Limiar | D maior ou igual a 0,10 com o n mínimo da aula — ou PSI na faixa "mudança" / "forte" |
| Ação | Congelar promoção do lote; inspecionar tema das imagens |
| Dono | Papel "dados / qualidade de entrada" |

## Checklist de saída

| Verificação | Sim / Não |
| :--- | :---: |
| As três linhas têm sinal + limiar + ação + dono | |
| Cada limiar é numérico ou faixa nomeada da aula (ex. PSI), com janela quando couber | |
| Cada dono é pessoa ou papel identificável (não "a equipe") | |
| Cada sinal aponta a uma pasta `NNN_*` praticada, ou a lacuna está explícita | |
| A seção de lacunas está escrita sem inventar cobertura | |
| Cada linha do contrato passa pelos cinco hábitos da Filosofia DevOps | |

## Bibliografia

Use estes textos ao preencher o contrato (links auditados em 2026-11-04):

1. **B1** — Google SRE, *Monitoring Distributed Systems* —
   <https://sre.google/sre-book/monitoring-distributed-systems/> —
   distingue página de sintoma e página de causa; o campo **sinal** desta
   aula é o sintoma.
2. **B6** — Prometheus, *Alerting best practices* —
   <https://prometheus.io/docs/practices/alerting/> —
   alerta precisa ser acionável; amarra **limiar** e **ação**.
3. **B7** — Prometheus, *The Zen of Prometheus* —
   <https://prometheus.io/docs/practices/the_zen/> —
   preferir poucos sinais claros a catálogo inchado — daí uma linha por fim.
4. **B9** — Rob Ewaschuk, *My Philosophy on Alerting* (espelho HTML) —
   <https://linuxczar.net/sysadmin/philosophy-on-alerting/> —
   quem atende e o que faz; justifica o campo **dono**.
5. **B11** — BentoML, *Metrics* —
   <https://docs.bentoml.org/en/latest/build-with-bentoml/observability/metrics.html> —
   de onde saem as séries deste Runtime quando a fonte é saúde.

### Para aprofundar

- **B2** — Google SRE, *Practical Alerting* —
  <https://sre.google/sre-book/practical-alerting/>
- **B3** — Google SRE, *Being On-Call* —
  <https://sre.google/sre-book/being-on-call/>
- **B4** — Google SRE Workbook, *Alerting on SLOs* —
  <https://sre.google/workbook/alerting-on-slos/>
- **B5** — Google SRE Workbook, *Monitoring* —
  <https://sre.google/workbook/monitoring/>
- **B8** — Prometheus, *Alerting rules* —
  <https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/>
- **B10** — Datadog, *Monitoring 101: Alerting* —
  <https://www.datadoghq.com/blog/monitoring-101-alerting/>
- Allspaw & Hammond (Velocity 2009) —
  <https://www.youtube.com/watch?v=LdOe18KhtT4>
- Sculley et al. (2015) —
  <https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf>
- Gartner AIOps (2017) —
  <https://www.gartner.com/en/newsroom/press-releases/2017-04-11-gartner-says-algorithmic-it-operations-drives-digital-business>
- Kreuzberger et al. (2023) —
  <https://ieeexplore.ieee.org/document/10069172>
- NVIDIA LLMOps —
  <https://developer.nvidia.com/blog/mastering-llm-techniques-llmops/>
- Picsellia CVOps —
  <https://www.picsellia.com/post/how-to-apply-mlops-to-computer-vision-cvops>

## Roteiro

| | Pasta |
| :--- | :--- |
| **Anterior** | [`008_psi_drift_alert_streamlit`](../008_psi_drift_alert_streamlit/README.md) |
| **Seguinte** | — |
