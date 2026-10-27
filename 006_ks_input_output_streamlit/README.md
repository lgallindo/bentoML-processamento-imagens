# Aula 006 — KS na entrada e na saída

## Por que estamos aqui

Um serviço pode responder **rápido** e com **HTTP 200** e, mesmo assim,
trabalhar sobre um mundo diferente do treino. A
[aula 003](../003_ks_drift_alert_streamlit/README.md) mede essa combinação
na luminância **L** das imagens **submetidas** e dispara um alerta sobre a
estatística **D** (Kolmogorov–Smirnov).

Aqui a pergunta se desdobra. O cliente manda uma imagem — isso é a
**entrada**. O serviço devolve outra — isso é a **saída**. Cada lado tem a
sua distribuição de L, a sua CDF, o seu **D**, o seu alerta.

Quando entrada e saída contam a mesma história, o filtro está **espelhando**
o uso. Quando a entrada parece estável e a saída não, algo no caminho de
inferência mudou (modelo trocado, pré-processamento, bug).

## L, histograma, CDF e D

Uma fotografia digital é uma grade de **pixels**. Em cores, cada pixel
carrega canais; para falar de claro/escuro, convertemos com
`Image.convert("L")`: **0** = preto, **255** = branco. Esse valor é a
luminância **L**.

O **histograma** conta quantos pixels caíram em cada faixa de L. A **CDF**
acumula, faixa a faixa, a fração do total até aquele ponto:

\[
F_k = \frac{1}{N}\sum_{i=0}^{k} h_i.
\]

Com duas CDFs \(F\) (referência) e \(G\) (lote),

\[
\delta_k = \lvert F_k - G_k \rvert,
\qquad
D = \max_k \delta_k.
\]

Nesta aula o eixo é **L por pixel** nos dois lados (entrada e saída).

## Dois alertas, uma regra

| Estado | Condição | Leitura |
| :--- | :--- | :--- |
| **INCONCLUSIVO** | \(n &lt; 8\) em qualquer lado daquele KS | Janela / lote ainda fino |
| **ALERTA** | \(n \ge 8\) e \(D \ge 0{,}10\) | Formas de L divergem naquele lado |
| **TRANQUILO** | \(n \ge 8\) e \(D &lt; 0{,}10\) | Compatível com a referência naquele lado |

O valor-p assintótico pode ser calculado; **não** entra na regra de alerta.

Em produção o lote é uma **caixa de tempo** (por exemplo pedidos dos
últimos 30 dias). Aqui os JSON em `batch_stats/` fazem o papel de uma
janela já agregada.

## Modo saudável e modo deslocado

No caminho **saudável**, a saída é só `convert("L")`. Entrada e saída
tendem a contar a mesma história:

| Lote | Entrada | Saída |
| :--- | :--- | :--- |
| control (praias 51–100) | TRANQUILO | TRANQUILO |
| forests | ALERTA | ALERTA (espelha o drift) |

No caminho **deslocado**, a saída soma **+40** em cada pixel de L (teto
255). Com o lote de **controle**, a entrada fica TRANQUILO e a saída
dispara ALERTA — a turma vê o contraste “pedidos ok, emissão estranha”.

## Objetivo operacional

1. Fixar referência de entrada e de saída a partir das mesmas 50 praias de
   treino (saída = filtro saudável).
2. Comparar lotes de controle e de florestas nos dois lados.
3. No Streamlit, ler os dois alertas e a leitura conjunta; experimentar o
   modo deslocado no controle.

## Estrutura da pasta

```text
006_ks_input_output_streamlit/
  README.md
  app.py                         # dois alertas + histogramas/CDFs
  service.py                     # /inference-grayscale e -shifted
  grayscale_model.py             # saudável + deslocado (+40)
  request_log.py                 # log entrada e saída (pair_id)
  io_pipeline.py                 # espelho offline do filtro
  alert_rule.py / ks_compare.py / histogram.py / …
  corpus_stats_input.json
  corpus_stats_output.json
  corpus_stats_output_shifted.json
  batch_stats/
    control_input.json
    control_output.json
    control_output_shifted.json
    forests_input.json
    forests_output.json
  scripts/
    extract_io_features.py
    build_corpus_io.py
    build_demo_batches_io.py
    verify_io_alerts.py
    save_grayscale_models.py
  tests/
  justfile
```

## Como executar

```bash
cd 006_ks_input_output_streamlit
# pasta da aula

just sync
# ambiente uv

just download-samples
# aponta samples/{beaches,forests}/ na raiz do repositório

just build-demo-batches-io
# regenera corpus_* e batch_stats/* (offline, sem servidor)

just verify-io-alerts
# imprime D/alerta entrada e saída no terminal

just streamlit
# http://localhost:8506
```

Com servidor (log vivo):

```bash
just save-models
just serve
# porta 3336 — /inference-grayscale e /inference-grayscale-shifted
```

## Testes

```bash
just test
```

## Comparação com a 003

A 003 olha só a **entrada**. Esta aula coloca a **saída** no mesmo aparelho
de alerta e mostra quando os dois lados divergem.

[`005_ks_anomaly_detection_streamlit`](../005_ks_anomaly_detection_streamlit/README.md)
· [`003_ks_drift_alert_streamlit`](../003_ks_drift_alert_streamlit/README.md)
