# Lição 04 — Kolmogorov–Smirnov: production contra corpus

## Objectivo

- Comparar a CDF agregada de **production** (log de `/inference-grayscale`) com a
  de **corpus** (treino) via estatística de **Kolmogorov–Smirnov**.
- Expor o resultado em `/monitor-ks-production-corpus-json`.
- Conservar inferência, histogramas corpus/production e o exercitador.
- Árvore **autocontida**: cópia independente do serviço base (raiz); **sem pesos neurais**.

## Comparação com a base

O serviço base não compara datasets. Esta lição introduz o pipeline `ks` sob o
prefixo `monitor-`.

**AS-IS (base)** — apenas filtros:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return image.convert("L")
```

**TO-BE (esta lição)** — KS sobre CDFs já agregadas:

```python
@bentoml.api(route="/monitor-ks-production-corpus-json")
def monitor_ks_production_corpus_json(
    self, channel: str = "L", bins: Positive = 256
) -> dict:
    return compare_production_to_corpus(channel=channel, bins=bins)
```

`ks_compare`: **D** = max |F_corpus − F_production|; **n_eff** a partir do número
de **imagens**; **p_value** pela aproximação assintótica clássica de KS.

| Rotas | Base | Esta lição |
| :--- | :---: | :---: |
| `/inference-{blur,grayscale,resize}` | sim | sim |
| `/monitor-histogram-corpus-{json,csv,image}` | não | sim |
| `/monitor-histogram-production-{json,csv,image}` | não | sim |
| `/monitor-ks-production-corpus-json` | não | sim |

## Utilização

### Conceitos mínimos

```text
/inference-{op}                         # grayscale | blur | resize
/monitor-{pipeline}-{dataset}-{repr}    # histogram | ks
```

```text
corpus_stats.json ──CDF──┐
                         ├── max |F_c − F_p| → statistic, p_value, n_eff
request_stats.json ─CDF──┘
```

Predefinição: `channel="L"`, `bins=256`. Porta: **3333**.

### Preparação

```bash
cd /home/lugatj/code/research/bentoML-processamento-imagens/04_ks_production_vs_corpus
just sync
just download-samples
just download-exerciser-samples
just extract-features
just build-corpus-stats
just save-grayscale-model
```

### Terminal 1 — servidor

```bash
just serve
```

### Terminal 2 — cliente

```bash
just exercise-grayscale
just build-request-stats
just curl-monitor-ks-production-corpus-json
just curl-monitor-histogram-corpus-json
just curl-monitor-histogram-production-json
```

Swagger: `just swagger`. Testes: `just test`.
