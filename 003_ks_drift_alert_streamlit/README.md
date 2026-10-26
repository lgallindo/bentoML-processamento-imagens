# Lição 003 — Alerta KS de drift (BentoML + Streamlit)

## Objetivo

- Tratar um tema de imagens como corpus de «treino» (sem treino neural).
- Enviar outro tema por `/inference-grayscale` com **log** em `request_features/`.
- No **Streamlit**, comparar a CDF de luminância (L) do corpus com a do lote de
  production via **Kolmogorov–Smirnov** e ver o banner
  ALERT / WATCH / QUIET / INCONCLUSIVE.
- Árvore **autocontida** (cópia do padrão BentoML + log); KS só no Streamlit.

## Entrada e saída

**Corpus (shipped):** primeiras 50 imagens de `samples/beaches/` (110 no tema) →
`corpus_stats.json` (`just extract-features && just build-corpus-stats`).

**Lotes demo (offline):** `just build-demo-batches` grava

- `batch_stats/control.json` — beaches 51–100 (mesmo tema)
- `batch_stats/forests.json` — 50 forests (tema divergente)

**Streamlit** — escolha o lote; vê D, p-value, n_eff, CDFs e miniaturas.

**Saída verificada nesta máquina (freeze shipped, n=50):**

| Lote | D (aprox.) | Banner |
| :--- | ---: | :--- |
| `forests` | ~0,23 | **WATCH** (D ≥ 0,10; p≈0,12 com n_eff por imagens) |
| `control` | ~0,05 | **QUIET** |

O «efeito magia negra» é o salto do banner e das CDFs quando o tema muda.
Com n_eff pelas **contagens de imagens**, o p-valor assintótico sobe devagar —
o D e o gráfico carregam o show. Prometheus / Grafana e alertas operacionais
ficam para lições posteriores.

**Regra do banner (v1):**

- **INCONCLUSIVE** se `n_images` &lt; 8 de qualquer lado
- **ALERT** se `p &lt; 0,05` **e** `D ≥ 0,10`
- **WATCH** se exactamente um dos dois dispara
- **QUIET** se nenhum dispara

**Contingência:** `just build-contingency-batches` (landscapes = beaches+forests,
production = 50 balls). Re-verificar D/p antes de mudar o handout — neste freeze
o par beaches→forests já separa por D; landscapes→balls pode sair QUIET em L.

## Como executar

```bash
cd 003_ks_drift_alert_streamlit
just sync
just download-samples          # aponta para samples/ na raiz
just extract-features
just build-corpus-stats
just build-demo-batches
just streamlit                 # http://localhost:8503
```

Caminho **com servidor** (log real):

```bash
just serve                     # terminal 1
just clear-request-features
just exercise-theme forests
just snapshot-batch forests    # → batch_stats/forests.json
just clear-request-features
just exercise-theme beaches --offset=12 --count=12
just snapshot-batch control
just streamlit
```

## O que acontece por dentro

```text
beaches[:12] → features/ → corpus_stats.json
forests (ou control) → /inference-grayscale → request_features/ → batch_stats/
Streamlit: CDF_L(corpus) vs CDF_L(lote) → D, p, n_eff → banner
```

`n_eff = n_c × n_p / (n_c + n_p)` com **n = número de imagens**.

## Comparação com a base

A base só devolve a imagem filtrada. Esta lição grava o pedido (como a linha
`020`) e analisa drift no Streamlit (sem rotas `/monitor-ks-*`).

## Testes

```bash
just test
```

[`004_prometheus_histcdf_streamlit`](../004_prometheus_histcdf_streamlit/README.md)
