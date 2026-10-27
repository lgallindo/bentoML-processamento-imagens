# Plano — anomalia KS em produção (ramo a partir da 003)

## Ideia

Reusar L → histograma → CDF → δ → **D** e o alerta \(D \ge 0{,}10\), mudando
a **unidade de monitoramento**:

| 003 (drift de lote) | 005 (anomalia) |
| :--- | :--- |
| Lote A vs lote B | Candidato (1 imagem) ou **janela temporal** vs referência fixa |
| Banner/alerta no lote completo | Alerta na janela; 1 imagem sozinha → INCONCLUSIVO |
| Sem relógio | **Time boxing** (ex.: últimos 30 dias de `request_features/`) |

## Produção (esqueleto)

1. Referência congelada (`corpus_stats.json` ou modelo de distribuição).
2. Cada `/inference-*` grava features com timestamp no nome.
3. Job periódico: filtra logs na janela → agrega histograma → **D** vs ref →
   alerta.
4. Painel: mesmo Streamlit didático, alimentado pela janela real.

## Critérios

- Controle (mesmo tema, janela cheia) → TRANQUILO.
- Florestas / bolas em volume ≥ 8 → ALERTA se D ≥ 0,10.
- Janela com &lt; 8 imagens → INCONCLUSIVO (não apitar).
