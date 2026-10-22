# Lição 002 — Histograma e CDF em Streamlit

## Objetivo

- Partir de uma **lista de números** e obter contagens por bin e a **CDF**.
- Ver o resultado num **app Streamlit**: tabela, gráfico Seaborn e amostras
  prontas.
- Usar **NumPy** para a matemática e **Seaborn** para o desenho.

## Comparação com a base

### O que o programa base faz

Na **raiz** do repositório há um serviço BentoML de filtros de **imagem**
(Pillow + anotações de tipo → HTTP). A entrada é um arquivo de foto; a saída é
outra imagem.

### O que esta lição acrescenta

Aqui a entrada é uma **lista de números**. Não há BentoML nem upload de imagem.
O app Streamlit coleta valores, chama o núcleo NumPy e mostra histograma + CDF
com Seaborn.

| Recurso | Base (raiz) | Esta lição |
| :--- | :--- | :--- |
| Entrada | imagem | lista de `float` |
| Interface | HTTP / Swagger | Streamlit |
| Gráfico | — | Seaborn (backend Matplotlib) |
| Matemática | filtros Pillow | `numpy.histogram` + CDF |

### Trecho decisivo

```python
payload = histogram_with_cdf([1, 2, 2, 5], bins=4)
fig = plot_histogram_cdf(payload["counts"], payload["edges"], payload["cdf"])
```

## Utilização

```bash
just sync
just app
```

Abra a URL que o Streamlit imprimir (porta **8502**). Cole números, ajuste
`bins`, ou use as amostras da barra lateral.

Testes:

```bash
just test
```

[`003_prometheus_histcdf_streamlit`](../003_prometheus_histcdf_streamlit/README.md)
