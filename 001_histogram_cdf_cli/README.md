# Lição 001 — Histograma e CDF na linha de comando

## Objetivo

- Partir de uma **lista de números** e obter contagens por bin e a **CDF**.
- Ver o resultado em **JSON**, **CSV** ou **PNG** (Seaborn).
- Usar **NumPy** para a matemática — sem BentoML e sem interface gráfica web.

## Comparação com a base

### O que o programa base faz

Na **raiz** do repositório há um serviço BentoML de filtros de **imagem**. A
entrada é um arquivo de foto; a saída é outra imagem (Pillow).

### O que esta lição acrescenta

Aqui a entrada é uma **lista de números**. O programa corre no terminal:
calcula histograma e CDF com NumPy e, se pedido, grava um gráfico Seaborn.

| Recurso | Base (raiz) | Esta lição |
| :--- | :--- | :--- |
| Entrada | imagem | lista de `float` |
| Interface | HTTP / Swagger | CLI (`just hist`) |
| Gráfico | — | Seaborn → PNG |
| Matemática | filtros Pillow | `numpy.histogram` + CDF |

### Trecho decisivo

```python
payload = histogram_with_cdf([1, 2, 2, 5], bins=4)
# payload["counts"], payload["edges"], payload["cdf"]
```

## Utilização

```bash
just sync
just hist --values='[1,2,2,5]' --bins=4
just hist --values='[1,2,2,5]' --bins=4 --format=csv
just hist --values='[1,2,2,5]' --bins=4 --format=image --output=histogram.png
just hist --values='[0,0.5,1,2.5,4]' --bins=4 --lo=0 --hi=4
```

Intervalo fixo rejeita valores fora de `[lo, hi]`.

Testes:

```bash
just test
```
