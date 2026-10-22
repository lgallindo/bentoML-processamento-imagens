# Lição 003 — Histograma e CDF a partir do Prometheus

## Objetivo

- Baixar os **buckets cumulativos** de latência que o Prometheus guarda a partir
  do `/metrics` do serviço BentoML na raiz do repositório.
- Montar **tabela**, **histograma** e **CDF** em Python (NumPy + Seaborn) num
  app Streamlit.
- Colocar o **quantil em Python** ao lado do **`histogram_quantile` em PromQL**
  (números e trechos de código) para comparar resultado e complexidade.

## Comparação com a base

### O que o programa base faz

Na **raiz** do repositório o BentoML serve filtros de imagem e publica métricas
HTTP em `/metrics`. O ficheiro `monitoring/prometheus.yml` configura o scrape;
`docs/prometheus.md` mostra como consultar p95 com PromQL.

### O que esta lição acrescenta

Aqui a entrada é a **série de buckets** já agregada pelo Prometheus (não a
imagem). O app pede esses números à API HTTP do Prometheus (ou a uma fixture
gravada), diferencia contagens cumulativas, desenha histograma + CDF e mostra
Python e PromQL lado a lado.

| Recurso | Base (raiz) | Esta lição |
| :--- | :--- | :--- |
| Entrada | imagem → `/metrics` | buckets Prometheus |
| Interface | HTTP / Swagger + Prometheus UI | Streamlit |
| Quantil | PromQL / Grafana | Python **e** PromQL |
| Gráfico | — (Grafana à parte) | Seaborn no app |

### Trecho decisivo

```python
samples = fetch_duration_buckets_from_fixture(endpoint="/grayscale")
payload = payload_from_samples(samples)
compare = compare_quantiles(
    payload["les"], payload["cumulative"], q=0.95, endpoint="/grayscale"
)
```

## Utilização

```bash
just sync
just app
```

Abra a URL do Streamlit (porta **8503**). O modo **fixture** funciona sem
Prometheus. Para o modo **live**:

1. Na raiz do repositório, suba o serviço (`just serve`) e o Prometheus como em
   `docs/prometheus.md` (URL típica `http://127.0.0.1:9090`).
2. Gere algum tráfego nos endpoints de inferência.
3. No app, escolha **live**, confirme a URL e clique em **Atualizar**.

A comparação numérica usa a forma **instantânea** (contadores cumulativos no
instante da query), alinhada ao espelho em Python:

```promql
histogram_quantile(0.95, sum by (le) (
  bentoml_service_request_duration_seconds_bucket{endpoint="/grayscale"}
))
```

A recording rule da raiz usa `rate(...[1m])`; o app também mostra essa variante
no painel de código, sem a usar por omissão.

Testes (só fixture / mocks, sem scrape):

```bash
just test
```

[`010_corpus_histograms_model`](../010_corpus_histograms_model/README.md)
