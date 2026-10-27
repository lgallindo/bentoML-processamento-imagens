# Aula 005 — Anomalia KS (candidato / janela vs referência)

Do mesmo aparelho da [aula 003](../003_ks_drift_alert_streamlit/README.md)
(L → histograma → CDF → δ → **D** → alerta) à pergunta de **produção**:
*este pedido (ou esta janela de pedidos) ainda parece o treino?*

O painel vivo está em [`app.py`](app.py).

## Sumário

1. [Por que estamos aqui](#1-por-que-estamos-aqui)
2. [HTTP verde ≠ dados adequados](#2-http-verde--dados-adequados)
3. [Definições (reuso da 003)](#3-definições-reuso-da-003)
4. [De drift de lote a anomalia](#4-de-drift-de-lote-a-anomalia)
5. [Time boxing](#5-time-boxing)
6. [Alerta sobre D (com janela)](#6-alerta-sobre-d-com-janela)
7. [Passo a passo — UI ≡ fórmula](#7-passo-a-passo--ui--fórmula)
8. [O experimento desta aula](#8-o-experimento-desta-aula)
9. [Estrutura da pasta](#9-estrutura-da-pasta)
10. [Como executar](#10-como-executar)
11. [Testes](#11-testes)
12. [Glossário](#12-glossário)
13. [Bibliografia](#13-bibliografia)

---

## 1. Por que estamos aqui

Na aula 003 o painel compara **dois lotes** já agregados (referência de
treino versus um lote nomeado de produção) e decide **ALERTA** /
**TRANQUILO** / **INCONCLUSIVO** sobre a estatística **D**.

Em operação real a pergunta muda de escala:

| Pergunta | Unidade típica |
| :--- | :--- |
| Drift de lote (003) | lote A vs lote B (ambos com \(n \ge 8\)) |
| Anomalia (005) | **uma** imagem candidata, ou a **janela** dos últimos *N* dias, vs referência fixa |

Uma foto isolada pode afastar a CDF e inflar **D**, mas **não** fecha o
alarme operacional: falta massa na janela. Por isso o modo «candidato»
desta aula mostra **D** e força **INCONCLUSIVO** quando \(n = 1\).

![Fluxo L → histograma → CDF → δ → D → alerta](../003_ks_drift_alert_streamlit/illustrations/01_workflow_l_to_alert.png)

---

## 2. HTTP verde ≠ dados adequados

O serviço BentoML desta pasta (mesmo espírito da 003) pode devolver
**200** com latência baixa enquanto o *conteúdo* das fotos deixa de
parecer o corpus de praias. Saúde da tubulação e adequação da
distribuição de luminância **L** são perguntas independentes — ver o
capítulo correspondente no handout da 003.

Aqui o monitoramento responde só à segunda: a forma de **L** no candidato
ou na janela ainda combina com `corpus_stats.json`?

---

## 3. Definições (reuso da 003)

| Símbolo | Significado |
| :--- | :--- |
| **L** | Cinza do pixel \(0\ldots255\) após `convert("L")` |
| **Histograma** | Contagens \(h_k\) por faixa de L |
| **CDF** | \(F_k=(1/N)\sum_{i\le k}h_i\) |
| **δ** | \(\delta_k=\lvert F^{\mathrm{ref}}_k-F^{\mathrm{cand}}_k\rvert\) |
| **D** | \(\max_k \delta_k\) |
| **Janela** | Pedidos cujo instante cai nos últimos *N* dias (ex.: 30) |

![CDFs dual (referência vs candidato/lote)](../003_ks_drift_alert_streamlit/illustrations/05_dual_cdf.png)

![δ(L) e D = max δ](../003_ks_drift_alert_streamlit/illustrations/06_delta_d.png)

---

## 4. De drift de lote a anomalia

| 003 (drift) | 005 (anomalia) |
| :--- | :--- |
| Lote A vs lote B | Candidato (1 imagem) **ou** janela temporal vs referência |
| Alerta com \(n\) dos dois lados | Alerta com \(n\) **na janela**; 1 imagem → INCONCLUSIVO |
| Sem relógio no exercício | **Time boxing** (política de *N* dias) |

O cálculo (histograma → CDF → δ → **D**) é o mesmo. Muda **quais**
imagens entram no lado «produção».

---

## 5. Time boxing

Em produção você **não** compara a referência com todo o histórico desde
o dia zero. Fixa um relógio — tipicamente pedidos dos **últimos 30 dias**.
Sem caixa de tempo, o lote mistura regimes antigos e novos e o **D**
perde significado operacional.

No exercício de sala, `batch_stats/*.json` é um **proxy** de janela já
agregada (`control`, `forests`, …). Em produção, `anomaly.py` filtra
`request_features/` pelo timestamp no nome do ficheiro.

---

## 6. Alerta sobre D (com janela)

| Estado | Quando | Leitura operacional |
| :--- | :--- | :--- |
| **INCONCLUSIVO** | \(n &lt; 8\) imagens **na janela** (ou candidato único) | Não há massa suficiente; **D** pode ser alto, mas o alarme não fecha |
| **ALERTA** | \(n \ge 8\) e \(D \ge 0{,}10\) | A forma de L na janela (ou lote proxy) afastou-se da referência |
| **TRANQUILO** | \(n \ge 8\) e \(D &lt; 0{,}10\) | Janela compatível com o treino nesta métrica |

[^p]: Valor-p assintótico pode ser calculado; fica fora da regra de alerta
(dependência entre pixels / graus de liberdade). Ver handout 003.

---

## 7. Passo a passo — UI ≡ fórmula

No Streamlit (`app.py`), cada bloco corresponde a um passo do ritual:

1. **Carregar referência** — `load_default_corpus_stats()` → contagens de L.
2. **Modo candidato** — histograma L da imagem → CDF → δ → **D**;
   `alert_on_d(D, n_images=1)` → **INCONCLUSIVO**.
3. **Modo lote/janela** — `compare_stats(ref, lote)` → **D**;
   `window_alert(n_lote, D)` → INCONCLUSIVO / ALERTA / TRANQUILO.
4. **Figuras** — histograma, CDF dual, curva δ com marca de **D**
   (mesmo espírito das ilustrações da 003).

Pseudocódigo alinhado ao painel:

```text
# Variáveis:
# ref — freeze corpus_stats.json (treino)
# cand — uma imagem OU agregação da janela
# D — max |F_ref − F_cand|

F_ref  ← CDF(histograma_L(ref))
F_cand ← CDF(histograma_L(cand))
D      ← max_k |F_ref[k] − F_cand[k]|
se n_janela < 8:
    estado ← INCONCLUSIVO
senão se D ≥ 0,10:
    estado ← ALERTA
senão:
    estado ← TRANQUILO
```

---

## 8. O experimento desta aula

Freeze típico (mesmos lotes da 003; ordem de grandeza do handout irmão):

| Caso | \(n\) | **D** (ordem) | Estado do alerta |
| :--- | ---: | :--- | :--- |
| Uma bola / floresta isolada | 1 | pode ser \(\gtrsim 0{,}10\) | **INCONCLUSIVO** (regra) |
| `batch_stats/control.json` (praias 51–100) | ≥ 8 | \(\approx 0{,}05\) | **TRANQUILO** |
| `batch_stats/forests.json` | ≥ 8 | \(\approx 0{,}23\) | **ALERTA** |

Confirme no painel (`just streamlit`): o modo candidato nunca deve
mostrar ALERTA operacional; o lote `forests` deve acender ALERTA; o
`control` deve permanecer TRANQUILO.

---

## 9. Estrutura da pasta

```text
005_ks_anomaly_detection_streamlit/
  app.py              # Streamlit (dois modos)
  anomaly.py          # score candidato/janela vs referência + time box
  alert_rule.py       # INCONCLUSIVO / ALERTA / TRANQUILO sobre D
  ks_compare.py       # KS de lotes (reuso 003)
  histogram.py        # L, histograma, CDF
  corpus_stats.json   # referência (mesmo freeze da 003)
  batch_stats/        # proxies de janela (control, forests, …)
  service.py          # BentoML grayscale + log (igual espírito 003)
  docs/PLAN_anomaly_production.md  # ponteiro → .local/plans/005/
  tests/test_anomaly.py
  illustrations/      # notas; figuras canónicas reusam 003
```

---

## 10. Como executar

```bash
cd 005_ks_anomaly_detection_streamlit
# pasta da aula

just sync
# ambiente uv

just sync-demo-from-003
# copia corpus_stats.json + batch_stats/ da aula 003

just streamlit
# http://localhost:8505
```

```bash
just test
# pytest da regra de anomalia e do time box
```

Plano de produção (instructor / gitignored):
[`.local/plans/005/PLAN_anomaly_production.md`](../../.local/plans/005/PLAN_anomaly_production.md)
(ponteiro na pasta: [`docs/PLAN_anomaly_production.md`](docs/PLAN_anomaly_production.md)).

---

## 11. Testes

`tests/test_anomaly.py` cobre score candidato, filtro de janela e a regra
de alerta com \(n &lt; 8\). Em mounts lentos (research loop), preferir
corridas unitárias focadas sem pipe para `tail`.

---

## 12. Glossário

| Termo | Definição curta |
| :--- | :--- |
| **Anomalia (nesta aula)** | Afastamento de L vs referência numa unidade pequena (candidato) ou numa janela |
| **Time boxing** | Restringir o lote de monitoramento a um intervalo de tempo |
| **INCONCLUSIVO** | \(n\) insuficiente na janela; não fechar alarme |
| **D** | Estatística KS \(\max\|F_{\mathrm{ref}}-F_{\mathrm{cand}}\|\) |

---

## 13. Bibliografia

Ver bibliografia KS / drift no handout da
[aula 003](../003_ks_drift_alert_streamlit/README.md#18-bibliografia).

[`003_ks_drift_alert_streamlit`](../003_ks_drift_alert_streamlit/README.md) ·
[`006_ks_input_output_streamlit`](../006_ks_input_output_streamlit/README.md) ·
[`000`](../000_mlops_pipelines_goals/README.md)
