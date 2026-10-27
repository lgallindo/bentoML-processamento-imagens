# Ramos planejados — lição 003 (KS drift)

Estado: rascunho de planejamento. A lição atual compara referência
(`samples/beaches/` como treino) com lotes homogêneos (`forests`, `control`).

## Ramo 1 — Lote de produção = praias + outro tema de paisagem

**Ideia.** Mesmo pipeline (histograma de L → CDF → δ → D → banner), mas o
lote de produção junta **praias e o outro conjunto de paisagem**
(`samples/forests/`) num único lote misto.

**Por quê.** Em produção o tráfego raramente é um tema puro. Misturar praias
com florestas no mesmo lote pergunta: o alerta KS ainda enxerga o afastamento
quando metade dos pedidos “parece” treino?

**Como (rascunho).**

1. Manter `corpus_stats.json` nas primeiras 50 praias (referência inalterada).
2. Montar produção com N imagens de `beaches/` (trecho fora do freeze) **mais**
   N imagens de `forests/` — por exemplo 25+25 ou 50+50.
3. Gravar `batch_stats/beaches+forests.json` (ou reusar o nome `landscapes`).
4. No Streamlit, escolher esse lote e ler D / banner como hoje.

**Critério de sucesso.** Documentar D e o banner desse lote misto ao lado de
`forests` puro e `control` puro, para a turma ver o efeito da mistura.

## Ramo 2 — (a definir)

Aguardando o segundo ramo. Placeholder até a próxima instrução.
