# Revisão histórica dos campos *Ops*

Material complementar da pasta
[`020_monitoring_contract`](README.md).
Não substitui o exercício do contrato
([`CONTRACT_TEMPLATE.md`](CONTRACT_TEMPLATE.md)):
aqui a pergunta é **de onde vieram** os rótulos DevOps, MLOps, CVOps,
LLMOps e AIOps, e **o que este repositório já cobre** (ou ainda não)
em cada um deles.

Ortografia e léxico: português do Brasil. Substantivos técnicos de
infraestrutura permanecem em inglês (Host, Endpoint, Container, Dashboard,
Scrape, Runtime).

---

## 1. Por que estes nomes se acumularam

Desde o fim dos anos 2000, a indústria de software tem anexado o sufixo
**Ops** a quase toda especialidade que precisa **entregar e manter** um
artefato em produção. O padrão retórico é o mesmo: pegar uma prática de
desenvolvimento (ou de ciência) e forçar o encontro com operação —
monitoramento, liberação, on-call, limiar, dono.

Os cinco rótulos abaixo **não** formam uma escada oficial. São camadas de
vocabulário que se sobrepõem:

| Rótulo | Objeto típico em produção | Pergunta-mãe |
| :--- | :--- | :--- |
| **DevOps** | Serviço de software (código + infra) | O pipeline responde e se libera com segurança? |
| **MLOps** | Modelo + dados + serving | Além de responder, o comportamento aprendido ainda merece confiança? |
| **CVOps** | Pipeline de visão (imagem/vídeo) | O mundo visual mudou? Anotação, GPU e drift de pixels? |
| **LLMOps** | Produto com modelo de linguagem | Prompt, contexto, custo e qualidade da geração ainda cabem no contrato? |
| **AIOps** | Telemetria da própria operação de TI | Dá para correlacionar e priorizar o dilúvio de alertas com algoritmos? |

Neste curso, a aula final da trilha
([aula 020](README.md))
amarra três fins já anunciados na
[aula 000](../000_mlops_pipelines_goals/README.md)
— saúde, drift, anomalia — a **sinal / limiar / ação / dono**.
Esses quatro campos são a gramática comum; os rótulos *Ops* são o mapa
histórico de **quem** costuma falar cada idioma.

---

## 2. DevOps (c. 2007–2009 → )

### Origem

O fio mais citado começa com a frustração de **Patrick Debois** entre
equipes de desenvolvimento e de operações (migrações de datacenter,
2007–2008) e com a conversa sobre *Agile Infrastructure* com
**Andrew Shafer** no Agile 2008 (Toronto). Em junho de 2009, no
[O’Reilly Velocity](https://conferences.oreilly.com/velocity),
**John Allspaw** e **Paul Hammond** (Flickr) apresentaram
[«10+ Deploys Per Day: Dev and Ops Cooperation at Flickr»](https://www.youtube.com/watch?v=LdOe18KhtT4)
(narrativa clássica: «não é o meu código, são as suas máquinas»). Debois,
inspirado pelo vídeo, organiza o primeiro
[devopsdays](https://devopsdays.org/)
em Ghent (2009); o nome **DevOps** consolida-se aí — ver relatos em
[devops.com — Origins](https://devops.com/the-origins-of-devops-whats-in-a-name/)
e em
[IT Revolution — Convergence of DevOps](https://itrevolution.com/articles/the-convergence-of-devops/).

### O que o campo passou a significar

Não é um produto. É a insistência em **liberar software com frequência**,
com automação de infra, observação e responsabilidade compartilhada entre
quem escreve e quem opera. Anos seguintes trouxeram CI/CD, containers,
SRE (Google), GitOps e *platform engineering* — sempre com a mesma
tensão: o serviço no ar versus o dedo apontado entre times.

Fontes de prática de alerta usadas nesta trilha (e citadas no
[README da 020](README.md#bibliografia)):

- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus — Alerting best practices](https://prometheus.io/docs/practices/alerting/)
- [Ewaschuk — My Philosophy on Alerting](https://linuxczar.net/sysadmin/philosophy-on-alerting/)

### Neste repositório

DevOps aparece como **saúde do pipeline**: processo no ar, HTTP, latência
(p95), `up`, regras em Prometheus. Prosa explícita nas seções «DevOps: o
serviço que responde» de
[`003`](../003_ks_drift_alert_streamlit/README.md)
e
[`008`](../008_psi_drift_alert_streamlit/README.md);
laboratório denso em
[`010_prometheus_promql`](../010_prometheus_promql/README.md),
[`016_grafana_dashboards`](../016_grafana_dashboards/README.md)
e irmãs de logs/vendors. O contrato da 020 pede **uma linha de saúde**
com dono — a herança DevOps sem sermão de «cinco hábitos».

---

## 3. MLOps (débito técnico ML 2015 → termo c. 2017–2018 → )

### Origem

O marco científico mais citado não inventa a palavra *MLOps*, mas define
o problema: Sculley et al.,
[«Hidden Technical Debt in Machine Learning Systems»](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf)
(NeurIPS 2015) — o retângulo preto do «modelo» é pequeno; o custo está no
código-cola, nas dependências de dados, nos consumidores não declarados e
nas mudanças do mundo externo. O léxico **MLOps** (machine learning +
DevOps) espalha-se em palestras, fornecedores e guias de nuvem por volta
de 2017–2018; sínteses posteriores incluem
[Kreuzberger, Kühl & Hirschl (IEEE Access, 2023)](https://ieeexplore.ieee.org/document/10069172)
e glossários como o da
[NVIDIA — MLOps](https://www.nvidia.com/en-us/glossary/mlops/).
Atenção: algumas páginas de marketing atribuem a **cunhagem** do termo ao
paper de 2015; o paper descreve a dívida, não batiza o campo — ver a
distinção em
[The Last Dictionary — MLOps](https://lastdictionary.com/mlops).

### O que o campo passou a significar

Tratar o sistema de ML como produto contínuo: versionar dados e modelos,
reproduzir treino, promover com critérios, **monitorar drift e qualidade**,
re-treinar quando o mundo mudar. DevOps sozinho mede se a API responde;
MLOps pergunta se a distribuição e o comportamento ainda são os do
contrato.

### Neste repositório

O título da trilha é MLOps
([`000_mlops_pipelines_goals`](../000_mlops_pipelines_goals/README.md)).
Os fins **drift** e **anomalia** (KS, PSI, janelas) são o núcleo
pedagógico de
[`003`](../003_ks_drift_alert_streamlit/README.md)–[`006`](../006_ks_mixed_landscape_streamlit/README.md),
[`008`](../008_psi_drift_alert_streamlit/README.md),
[`004`](../004_ks_anomaly_detection_streamlit/README.md)
e dos tijolos
[`011`](../011_corpus_histograms_model/README.md)–[`014`](../014_ks_production_vs_corpus/README.md).
Serving: BentoML + `/metrics`
([`009`](../009_bentoml_oci_runtime/README.md),
[docs BentoML Metrics](https://docs.bentoml.org/en/latest/build-with-bentoml/observability/metrics.html)).
A 020 fecha pedindo **três linhas** — saúde (DevOps), drift e anomalia
(MLOps) — no mesmo formulário.

---

## 4. CVOps (visão computacional × MLOps; c. final dos anos 2010 → )

### Origem

**CVOps** (*Computer Vision Operations*) é rótulo de mercado e de
fornecedores para «MLOps quando o dado é imagem ou vídeo»: arquivos
binários grandes, anotação como etapa de primeira classe, GPU, edge, e
drift visual (iluminação, câmera, tema) que métricas tabulares genéricas
não capturam sozinhas. Introduções públicas incluem
[Picsellia — Introducing CVOps](https://www.picsellia.com/post/how-to-apply-mlops-to-computer-vision-cvops),
[Picsellia — MLOps for Computer Vision](https://www.picsellia.com/post/mlops-for-computer-vision-complete-guide)
e narrativas de edge como
[Xailient — CVOps](https://xailient.com/blog/xailient-created-cvops-for-edge-computer-vision-at-scale/).
Não há um «paper fundador» canônico comparável ao de Sculley; o termo
compõe-se por especialização de domínio.

### O que o campo passou a significar

Gestão do lago de imagens, campanhas de label, treino em GPU, deploy
(cloud/edge) e monitoramento do **mundo visual** — não só da latência do
Endpoint.

### Neste repositório

O curso **é** um laboratório de visão enxuto (grayscale, luminância L,
histogramas, beaches/forests), mas o handout estudante **quase nunca
escreve a palavra CVOps**. O conteúdo CVOps está implícito nos sinais de
drift sobre imagens; a nomenclatura pública do repo permanece **MLOps** +
DevOps. Isso é intencional: menos jargão novo nesta aula; mais contrato
preenchível.

---

## 5. LLMOps (c. 2022–2024 → )

### Origem

Com a adoção em massa de modelos de linguagem, o mercado nomeou
**LLMOps** (e, em alguns glossários, *GenAIOps* / *RAGOps*) para o
subconjunto de operação centrado em prompts, contexto, recuperação,
avaliação de geração, custo por token e troca de fornecedor de modelo
fundacional. Ver, por exemplo,
[NVIDIA — Mastering LLM Techniques: LLMOps](https://developer.nvidia.com/blog/mastering-llm-techniques-llmops/)
(hierarquia MLOps ⊃ GenAIOps ⊃ LLMOps).

### O que o campo passou a significar

Os quatro campos da 020 ainda valem (sinal, limiar, ação, dono), mas os
**sinais** mudam: taxa de recusa, similaridade de embedding da resposta,
custo, latência do provedor, regressão de um banco de prompts — não D de
KS sobre luminância.

### Neste repositório

**Fora de escopo da trilha atual.** Não há pasta `NNN_*` de prompt
eval, RAG ou gateway LLM. Qualquer plano futuro de LLMOps seria
**novo ato**, não extensão silenciosa da 020.

---

## 6. AIOps (Gartner, 2017 → )

### Origem

Em abril de 2017 a Gartner populariza **AIOps** a partir de *algorithmic
IT operations* — plataformas que ingerem telemetria operacional, aplicam
analytics/ML e apoiam correlação, priorização e (eventualmente)
remediação. Comunicado de imprensa:
[«Gartner Says Algorithmic IT Operations Drives Digital Business»
(2017-04-11)](https://www.gartner.com/en/newsroom/press-releases/2017-04-11-gartner-says-algorithmic-it-operations-drives-digital-business).
Distinção útil face a MLOps:
[Opensource.com — AIOps vs MLOps](https://opensource.com/article/21/2/aiops-vs-mlops)
(AIOps opera **sobre** a operação de TI; MLOps opera **o ciclo de vida do
modelo**).

### O que o campo passou a significar

Reduzir o dilúvio de eventos: correlacionar alertas, detectar anomalias
em séries de infra, sugerir causa. Não substitui o contrato humano de
dono — apenas tenta filtrar o que chega ao humano.

### Neste repositório

Há um **eco didático** de «anomalia» (aula
[`004`](../004_ks_anomaly_detection_streamlit/README.md),
janela vs referência, INCONCLUSIVO por n pequeno) e alertas clássicos
Prometheus (média ± k σ no p95). Isso **não** é uma plataforma AIOps:
não há correlação multi-fonte automática, topologia, nem motor de
ingestão cross-domain. A análise didática interna do monorepo (arquivo local
`.local/handoff/ANALISE-DIDATICA-AULAS-003-008.md`, §2.4 — fora do Git
público) fala em «ponte DevOps / MLOps / AIOps» no sentido
**pedagógico** (por que instrumentar pedidos), não como entrega de
produto AIOps.

---

## 7. Como a aula 020 corta o mapa

| Campo da 020 | Eco *Ops* predominante | Fonte típica na trilha |
| :--- | :--- | :--- |
| Linha de **saúde** | DevOps (+ fatia SRE/Prometheus) | `010`, regras/UI de alertas |
| Linha de **drift** | MLOps (e CVOps implícito) | `003`, `008`, `014` |
| Linha de **anomalia** | MLOps; eco fraco de AIOps | `004` |
| Lacunas conscientes | Honestidade operacional (todos os *Ops*) | lab SKIP, sinal não visto |

A parábola do README (p95 `firing` com HTTP 200; lote KS/PSI com serviço
ainda convertendo) é exatamente a fronteira DevOps × MLOps/CVOps: saúde
do pipeline versus adequação do mundo de entrada.

---

## 8. Planos e lacunas — o que o trabalho interno ainda não concluiu

Varredura em arquivos **locais** do clone (`.local/plans/`,
`.local/handoff/`, `.local/AGENT_PLANS.md` — gitignored; não aparecem no
GitHub), em 2026-11-04, filtrada aos cinco campos e à aula 020.

### 8.1 Explicitamente diferido ou só proposta

| Plano / nota (path no clone) | Estado | Relação com *Ops* |
| :--- | :--- | :--- |
| `.local/plans/PLAN_20261104T141331Z_semver_service_version_and_lesson001.md` | **deferred** — aguarda ordem «execute o plano» | DevOps/MLOps de serving: `service_version` real em `/metrics`; sweep LESSON-001 em 000–020 |
| `.local/plans/PLAN_20261028T140500Z_003_worked_examples_all_sections.md` | **proposta** («implementação completa = onda futura»); §12 parcial | Exemplos trabalhados DevOps (§2) e MLOps (§3) na 003 ainda não como onda completa |
| `.local/plans/005/PLAN_anomaly_production.md` | esqueleto de produção (job + janela real) | Anomalia MLOps «de verdade» além do teatro Streamlit — não fechado como pipeline de produção |
| Livrinho 020 com «Filosofia DevOps» + cinco hábitos + catálogo mega | **superseded** pelo contrato concreto (`8c40b35`) | DevOps-sermão removido do README estudante de propósito |

### 8.2 Ausência de plano (não há *unimplemented plan* porque não há plan)

| Tema | Achado |
| :--- | :--- |
| **LLMOps** | Nenhum `PLAN_*` nem pasta `NNN_*` dedicada a prompt/RAG/LLM no monorepo |
| **CVOps** como rótulo de handout | Nenhum plano para renomear a trilha; conteúdo visual existe sob rótulo MLOps |
| **AIOps** como plataforma | Nenhum plano de correlacionador multi-fonte; só eco de anomalia/alerta |
| Seção histórica dos cinco *Ops* na 020 | **Esta nota** (`CAMPOS_OPS.md`) — não existia antes; o README da 020 permanece curto |

### 8.3 Já entregue (não confundir com pendência)

| Item | Evidência |
| :--- | :--- |
| Aula 020 (contrato sinal/limiar/ação/dono) | Commit `8c40b35`; [README](README.md) |
| Catálogo aula→sinal fora do handout | `.local/handoff/NOTE_20261104T182000Z_020_PROVENIENCIA_SINAIS.md` |
| Arco DevOps→MLOps nas 003/008 | Seções 2–3 dos READMEs; uplift estrutural 008 portou a prosa |
| Aulas 021/022 (UI regras/alertas Prometheus) | Pastas presentes na árvore; plano de screenshots 021 marcado done (Path B) |

### 8.4 Working tree residual (fora desta entrega)

Edits LESSON-001 em várias `NNN_*` e `docs/ports.md` podem permanecer
**sujos e não commitados** no clone local (nota
`.local/handoff/NOTE_20261104T205500Z_020_REWRITE_FECHO_SHIPPED.md`).
Isso é higiene de handout, não um quinto *Ops*.

---

## 9. Leitura sugerida (ordem)

1. Allspaw & Hammond (Velocity 2009) — cooperação Dev/Ops
   ([vídeo](https://www.youtube.com/watch?v=LdOe18KhtT4)).
2. Debois / devopsdays —
   [devopsdays.org](https://devopsdays.org/).
3. Sculley et al. (2015) —
   [PDF NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf).
4. Gartner (2017) — AIOps / algorithmic IT operations
   ([press release](https://www.gartner.com/en/newsroom/press-releases/2017-04-11-gartner-says-algorithmic-it-operations-drives-digital-business)).
5. Kreuzberger et al. (2023) — overview MLOps
   ([IEEE](https://ieeexplore.ieee.org/document/10069172)).
6. NVIDIA LLMOps —
   [blog](https://developer.nvidia.com/blog/mastering-llm-techniques-llmops/).
7. Picsellia CVOps —
   [intro](https://www.picsellia.com/post/how-to-apply-mlops-to-computer-vision-cvops).
8. Voltar ao exercício:
   [README 020](README.md) →
   [CONTRACT_TEMPLATE.md](CONTRACT_TEMPLATE.md).

---

*Documento de apoio histórico e de inventário de planos. Critério de
conclusão da aula 020 continua sendo o artefato preenchido (Sim/Não no
README), não a memorização desta cronologia.*
