# Lição 001 — Histograma e CDF na linha de comando

## Objetivo

Transformar uma **lista de números** em:

1. um **histograma** (contagens por intervalo, ou *bin*);
2. a **função de distribuição acumulada (CDF)** correspondente, com valores em
   `[0, 1]`;
3. o mesmo resultado em **JSON**, **CSV** ou um **PNG** (barras + curva da CDF).

Tudo corre no terminal, com NumPy na matemática e Seaborn no gráfico.

## Entrada e saída

### Exemplo principal

**Entrada:** quatro valores e quatro bins — o intervalo é inferido do mínimo e
do máximo (`[1, 5]`):

```bash
just hist --values='[1,2,2,5]' --bins=4
```

**Saída (JSON):**

```json
{
  "n": 4,
  "bins": 4,
  "range": [1.0, 5.0],
  "counts": [1, 2, 0, 1],
  "edges": [1.0, 2.0, 3.0, 4.0, 5.0],
  "cdf": [0.25, 0.75, 0.75, 1.0]
}
```

Leitura rápida:

| Campo | Significado neste exemplo |
| :--- | :--- |
| `edges` | Bordas dos quatro bins de largura 1: `[1,2)`, `[2,3)`, `[3,4)`, `[4,5]` |
| `counts` | `1` cai no 1.º bin; os dois `2` no 2.º; ninguém no 3.º; `5` no 4.º |
| `cdf` | Fração acumulada: após o 2.º bin já temos 75 % dos pontos; no fim, `1.0` |

A soma de `counts` é `n` (aqui, 4). O último valor de `cdf` é sempre `1.0`
quando há pelo menos uma observação.

**Mesmos dados em CSV:**

```bash
just hist --values='[1,2,2,5]' --bins=4 --format=csv
```

```text
bin,left,right,count,cdf
0,1.0,2.0,1,0.25
1,2.0,3.0,2,0.75
2,3.0,4.0,0,0.75
3,4.0,5.0,1,1.0
```

**Gráfico:**

```bash
just hist --values='[1,2,2,5]' --bins=4 --format=image --output=histogram.png
```

Abra `histogram.png`: barras das contagens e, no eixo direito, a CDF.

### Intervalo fixo e rejeição

Com `--lo` e `--hi`, o intervalo deixa de ser inferido. Valores fora dele
interrompem o programa com mensagem clara:

```bash
just hist --values='[0,0.5,1,2.5,4]' --bins=4 --lo=0 --hi=4
```

→ `counts` `[2, 1, 1, 1]` (dois pontos em `[0,1)`, depois um em cada bin
seguinte).

```bash
just hist --values='[1,9]' --bins=2 --lo=0 --hi=5
```

→ `valor fora do intervalo [0.0, 5.0]: 9.0`

### Parâmetros úteis

| Flag | Função |
| :--- | :--- |
| `--values` | JSON list ou números separados por vírgula |
| `--file` | Mesmo conteúdo lido de um arquivo texto |
| `--bins` | Número de bins (padrão 10) |
| `--lo` / `--hi` | Intervalo fechado opcional (usar os dois juntos) |
| `--format` | `json` (padrão), `csv` ou `image` |
| `--output` | Arquivo de saída (obrigatório na prática para PNG) |

## Como executar

Na pasta desta lição:

```bash
just sync
just hist --values='[1,2,2,5]' --bins=4
just hist --values='[1,2,2,5]' --bins=4 --format=csv
just hist --values='[1,2,2,5]' --bins=4 --format=image --output=histogram.png
just hist --values='[0,0.5,1,2.5,4]' --bins=4 --lo=0 --hi=4
```

(O `just` trata vírgula como separador de argumentos: mantenha o JSON entre
aspas simples, como acima.)

Testes automatizados:

```bash
just test
```

## O que acontece por dentro

### Fluxo

```text
--values / --file
        │
        ▼
  lista de float
        │
        ▼
 histogram_from_values   →  counts[], edges[]     (NumPy)
        │
        ▼
 cdf_from_counts         →  cdf[]                 (cumsum / total)
        │
        ├── format=json  →  stdout / arquivo
        ├── format=csv   →  linhas bin,left,right,count,cdf
        └── format=image →  plot_histogram_cdf    (Seaborn) → PNG
```

Funções em `histcdf.py`: `histogram_from_values`, `cdf_from_counts`,
`histogram_with_cdf`. Desenho em `plotting.plot_histogram_cdf`. A CLI está em
`hist_cli.py`.

### Algoritmo

**Histograma.** Dado o intervalo `[lo, hi]` (inferido ou passado) e `bins`
bins de largura igual, cada valor cai num índice de bin; o extremo direito
`hi` entra no último bin. Contagens fora de `[lo, hi]` não são ignoradas em
silêncio: o código levanta erro.

**CDF.** A partir das contagens:

```text
# Variáveis:
# counts — lista de contagens por bin (inteiros ≥ 0)
# total  — soma de counts
# running — acumulado parcial
# cdf    — lista de frações em [0, 1]

total ← soma(counts)
se total = 0: erro
running ← 0
cdf ← []
para cada c em counts:
    running ← running + c
    cdf.acrescentar(running / total)
# cdf[-1] = 1.0
```

No código: `cdf_from_counts` faz `np.cumsum(counts) / counts.sum()`.

[`002_histogram_cdf_streamlit`](../002_histogram_cdf_streamlit/README.md)
