# Aula 020 — Contrato de monitoramento (fecho)

**Conceito desta aula:** fechar a trilha preenchendo **uma página** que amarra
os três fins de monitoramento da
[`000_mlops_pipelines_goals`](../000_mlops_pipelines_goals/README.md) —
**saúde do servidor**, **drift de dados**, **detecção de anomalias** — a
quatro campos: **sinal**, **limiar**, **ação** e **dono**. Esta pasta não
sobe serviço novo e não pede Dashboard nem Scrape; você cita sinais que já
praticou nas aulas anteriores.

Modelo: [`CONTRACT_TEMPLATE.md`](CONTRACT_TEMPLATE.md).

## O que quebra sem dono

Na aula de PromQL, o p95 do Endpoint de grayscale dispara (`firing`) enquanto
o HTTP continua 200: a imagem sai, o cliente não vê erro, e o painel de
sucesso permanece verde. No mesmo curso, um lote de paisagens em KS ou PSI
cruza o limiar de drift frente ao corpus — o serviço ainda converte; só o
mundo de entrada mudou.

Se o limiar existe sem **ação** e sem **dono**, os dois eventos viram o mesmo
aviso órfão: alguém vê o número, ninguém decide o próximo passo, e o pipeline
segue «saudável» na superfície. O contrato existe para impedir esse vazio —
uma linha por fim, com responsável nomeado.

## Quatro campos

| Campo | Pergunta que responde | Eco na bibliografia |
| :--- | :--- | :--- |
| **Sinal** | O que se mede, com nome de série ou estatística? | Página de sintoma (B1): o que o operador vê primeiro |
| **Limiar** | A partir de qual valor e janela isso está errado? | Alerta acionável (B6, B9): quando agir, não «algo mudou» |
| **Ação** | Qual o próximo passo concreto se o limiar for cruzado? | Mesma linha: o alerta muda uma decisão |
| **Dono** | Quem executa essa ação (pessoa ou papel real)? | Filosofia de alerta (B9): alguém atende; «a equipe» não atende |

Cada fim da trilha (saúde, drift, anomalia) recebe **uma** linha com esses
quatro campos. «Muito alto» e «anormal» não bastam — o dono ficaria sem
critério.

## Escopo Negativo

| Isto **não** é o contrato | Por quê |
| :--- | :--- |
| Montar ou polir um Dashboard | Dashboard mostra séries; não registra dono nem ação |
| Colar o dump de `GET /metrics` | O texto cru lista famílias; o contrato escolhe **um** sinal por fim |
| Preencher formulário sem sinal praticado | Inventar limiar elegante sem ter visto o gráfico ou o painel |
| Subir Container, Prometheus ou Grafana nesta pasta | Fecho textual; portas e Scrape ficam nas aulas que os operam |
| Cumprir «cinco hábitos» genéricos | O critério de saída é o artefato preenchido, não um sermão |

## Como proceder

1. Abra [`CONTRACT_TEMPLATE.md`](CONTRACT_TEMPLATE.md) (copie para um arquivo
   local se quiser versionar a sua versão fora do Git do curso).
2. Preencha **três linhas** — uma por fim — com sinais cuja **fonte** seja
   uma pasta `NNN_*` que você de fato praticou. Fontes típicas (não é
   inventário completo):
   - Saúde: `010_prometheus_promql` (p95, `up`, taxa)
   - Drift: `003_ks_drift_alert_streamlit` ou `008_psi_drift_alert_streamlit`
   - Anomalia: `004_ks_anomaly_detection_streamlit`
3. Na seção de lacunas, declare o que ficou de fora (lab SKIP, sinal não
   observado) e o impacto — escreva «não disponível»; não invente cobertura.

### Exemplo trabalhado (saúde)

| Campo | Exemplo |
| :--- | :--- |
| Sinal | p95 de `bentoml_service_request_duration_seconds` no job da aula |
| Fonte | `010_prometheus_promql` |
| Limiar | p95 acima da linha de base da regra do repositório por pelo menos 1 min |
| Ação | Investigar Endpoint lento; reduzir carga; checar Container |
| Dono | Papel «plantão do serviço» (nomeie uma pessoa da turma ou do lab) |

### Exemplo trabalhado (drift)

| Campo | Exemplo |
| :--- | :--- |
| Sinal | Estatística D (KS) do lote frente à referência — ou PSI na faixa da aula |
| Fonte | `003_ks_drift_alert_streamlit` ou `008_psi_drift_alert_streamlit` |
| Limiar | D maior ou igual a 0,10 com o n mínimo da aula — ou PSI na faixa «mudança» / «forte» |
| Ação | Congelar promoção do lote; inspecionar tema das imagens |
| Dono | Papel «dados / qualidade de entrada» |

## Conclusão (autoavaliação)

Marque **Sim** ou **Não** sozinho — sobre o artefato que você preencheu.

| Verificação | Sim / Não |
| :--- | :---: |
| As três linhas têm sinal + limiar + ação + dono | |
| Cada limiar é numérico ou faixa nomeada da aula (ex. PSI), com janela quando couber | |
| Cada dono é pessoa ou papel identificável (não «a equipe») | |
| Cada sinal aponta a uma pasta `NNN_*` praticada, ou a lacuna está explícita | |
| A seção de lacunas está escrita sem inventar cobertura | |

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

## Roteiro

| | Pasta |
| :--- | :--- |
| **Anterior** | [`008_psi_drift_alert_streamlit`](../008_psi_drift_alert_streamlit/README.md) |
| **Seguinte** | — |
