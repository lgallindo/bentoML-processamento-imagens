# Aula 005 — Anomalia KS (candidato / janela vs referência)

## Por que esta aula

A [aula 003](../003_ks_drift_alert_streamlit/README.md) compara **dois
lotes** e alerta sobre **D**. Em produção muitas vezes a pergunta é outra:
*este pedido (ou esta semana de pedidos) ainda parece o treino?*

Aqui o mesmo aparelho — **L** → histograma → CDF → δ → **D** — vira
**detecção de anomalia** com **time boxing**.

## Definições (reuso da 003)

| Símbolo | Significado |
| :--- | :--- |
| **L** | Cinza do pixel \(0\ldots255\) após `convert("L")` |
| **Histograma** | Contagens \(h_k\) por faixa de L |
| **CDF** | \(F_k=(1/N)\sum_{i\le k}h_i\) |
| **D** | \(\max_k\|F^{\mathrm{ref}}_k-F^{\mathrm{cand}}_k\|\) |
| **Janela** | Pedidos cujo instante cai nos últimos *N* dias (ex.: 30) |

## Alerta sobre D (com time boxing)

| Estado | Quando | Leitura operacional |
| :--- | :--- | :--- |
| **INCONCLUSIVO** | \(n &lt; 8\) imagens **na janela** (ou candidato único) | Não há massa suficiente no time box; **D** pode ser alto, mas o alarme não fecha |
| **ALERTA** | \(n \ge 8\) e \(D \ge 0{,}10\) | A forma de L na janela (ou lote proxy) afastou-se da referência |
| **TRANQUILO** | \(n \ge 8\) e \(D &lt; 0{,}10\) | Janela compatível com o treino na métrica desta aula |

**Time boxing.** Em produção você **não** compara a referência com todo o
histórico desde o dia zero. Fixa um relógio — tipicamente *imagens / pedidos
dos últimos 30 dias* (ou última semana, último turno). Sem caixa de tempo, o
lote mistura regimes antigos e novos e o **D** perde significado operacional.

[^p]: Valor-p assintótico pode ser calculado; fica fora da regra de alerta
(dependência entre pixels / graus de liberdade). Ver handout 003.

## O que o Streamlit faz

1. **Uma imagem candidata** (ex.: bola) vs `corpus_stats.json` → mostra **D**;
   alerta operacional = INCONCLUSIVO (\(n=1\)).
2. **Lote** em `batch_stats/` (proxy de janela) vs referência → alerta com a
   tabela acima (`forests` tipicamente ALERTA; `control` TRANQUILO).

## Estrutura da pasta

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
  docs/PLAN_anomaly_production.md
  tests/test_anomaly.py
```

## Como executar

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

Plano de produção:
[`docs/PLAN_anomaly_production.md`](docs/PLAN_anomaly_production.md).

[`003_ks_drift_alert_streamlit`](../003_ks_drift_alert_streamlit/README.md) ·
[`006_ks_input_output_streamlit`](../006_ks_input_output_streamlit/README.md) ·
[`000`](../000_mlops_pipelines_goals/README.md)
