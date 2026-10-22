# Lição 002 — Histograma e CDF em Streamlit

## Objetivo

Ver o mesmo objeto da linha de comando — **histograma + CDF** de uma lista de
números — num **app Streamlit**: você cola valores (ou carrega um CSV), ajusta
`bins` e o intervalo, e a página atualiza a **tabela** e o **gráfico** Seaborn.

A matemática está em `histcdf.py` (NumPy); o desenho em `plotting.py` (Seaborn).

## Entrada e saída

### Exemplo principal

**Entrada** (área de texto do app, ou botão «Amostra uniforme» / «Amostra
normal» na barra lateral):

```text
1, 2, 2, 5
```

Com **bins = 4** e intervalo automático:

**Saída — métricas:** `n = 4`, mínimo `1`, máximo `5`.

**Saída — tabela** (colunas `bin`, `left`, `right`, `count`, `cdf`):

| bin | left | right | count | cdf |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1.0 | 2.0 | 1 | 0.25 |
| 1 | 2.0 | 3.0 | 2 | 0.75 |
| 2 | 3.0 | 4.0 | 0 | 0.75 |
| 3 | 4.0 | 5.0 | 1 | 1.0 |

**Saída — gráfico:** barras das contagens; no eixo direito, a CDF (mesmos
centros de bin). O botão **Baixar PNG** grava essa figura.

### Intervalo fixo

Na barra lateral, marque **Fixar intervalo [lo, hi]** e defina, por exemplo,
`lo = 0`, `hi = 4` com valores `0, 0.5, 1, 2.5, 4`. As contagens passam a
`[2, 1, 1, 1]`. Se algum valor cair fora de `[lo, hi]`, o app mostra o erro
em vermelho e não desenha o gráfico.

### Upload CSV

Opcional: envie um CSV cuja **primeira coluna** seja numérica (cabeçalho
`value` / `x` / etc. é ignorado). Os números dessa coluna substituem a área de
texto.

### Controles

| Controlo | Efeito |
| :--- | :--- |
| Slider `bins` | Resolução do histograma (1–50) |
| Fixar `[lo, hi]` | Usa intervalo declarado em vez do min/max dos dados |
| Amostra uniforme / normal | Preenche a área de texto com 200 pontos sintéticos |
| Baixar PNG | Exporta o gráfico atual |

## Como executar

Na pasta desta lição:

```bash
just sync
just app
```

O Streamlit sobe em **http://127.0.0.1:8502** (porta configurada no `justfile`).
Abra o URL impresso no terminal, cole `1, 2, 2, 5`, deixe `bins = 4` e confira
a tabela e o gráfico acima.

Testes:

```bash
just test
```

## O que acontece por dentro

### Fluxo

```text
textarea / CSV / amostra
        │
        ▼
  parse → array NumPy
        │
        ▼
 histogram_with_cdf(values, bins, value_range?)
        │
        ├── métricas (n, min, max)
        ├── st.dataframe (bin, left, right, count, cdf)
        └── plot_histogram_cdf → st.pyplot (+ download PNG)
```

`app.py` só coleta entrada e renderiza. O cálculo é
`histogram_with_cdf` → `histogram_from_values` + `cdf_from_counts` em
`histcdf.py`.

### Algoritmo

Igual ao núcleo numérico desta pasta:

1. **Bins de largura igual** em `[lo, hi]` (inferido ou fixo) via
   `numpy.histogram`; valor fora do intervalo → erro explícito.
2. **CDF:** `cdf[i] = sum(counts[:i+1]) / sum(counts)`, com último termo `1.0`.

```text
# Variáveis:
# values — array 1-D de float
# bins   — número de intervalos
# lo, hi — extremos do eixo
# counts, edges — saída de np.histogram
# cdf — cumsum(counts) / sum(counts)

(counts, edges) ← histogram_from_values(values, bins, value_range=(lo, hi)?)
cdf ← cdf_from_counts(counts)
```

O gráfico usa os **centros** `(edges[i]+edges[i+1])/2` para alinhar barras e
pontos da CDF.

[`003_prometheus_histcdf_streamlit`](../003_prometheus_histcdf_streamlit/README.md)
