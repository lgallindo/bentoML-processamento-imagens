# Lição 03 — Histogramas do log de pedidos e exercitador

## Objectivo

- Agregar `request_features/` em `request_stats.json` e **reportar** histogramas
  de production (`/monitor-histogram-production-*`), gémeos dos do corpus.
- Separar **download offline** do exercitador (`bentoml-exer-*`) da **submissão
  cronometrada** a `/inference-grayscale`.
- Árvore **autocontida**: cópia independente do serviço base (raiz); **sem pesos neurais**.

## Comparação com a base

O serviço base não regista pedidos nem expõe monitorização. Esta lição acrescenta
o par corpus/production e o exercitador.

**AS-IS (base)** — só inferência:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return image.convert("L")
# (sem monitor-*)
```

**TO-BE (esta lição)** — log + relatórios production:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    log_grayscale_submission(image)
    return self._grayscale_model(image)

@bentoml.api(route="/monitor-histogram-production-json")
def monitor_histogram_production_json(self, channel: str = "L", bins: Positive = 256) -> dict:
    return report_request_histogram_json(channel=channel, bins=bins)
# + csv / image; corpus permanece em /monitor-histogram-corpus-*
```

| Rotas | Base | Esta lição |
| :--- | :---: | :---: |
| `/inference-{blur,grayscale,resize}` | sim | sim |
| `/monitor-histogram-corpus-{json,csv,image}` | não | sim |
| `/monitor-histogram-production-{json,csv,image}` | não | sim |

## Utilização

### Conceitos mínimos

```text
samples/train_*.jpg            seeds  bentoml-edu-N    (corpus)
exerciser_samples/exer_*.jpg   seeds  bentoml-exer-N   (exercitador)
```

Não misturar os dois conjuntos. Predefinição: `channel="L"`, `bins=256`. Porta: **3333**.

```text
download-exerciser-samples  →  exerciser_samples/   (offline, sem servidor)
exercise-grayscale          →  POST /inference-grayscale  (só submete; imprime tempos)
build-request-stats         →  request_stats.json
```

### Preparação

```bash
cd /home/lugatj/code/research/bentoML-processamento-imagens/03_request_log_histograms
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
just curl-monitor-histogram-production-json
just curl-monitor-histogram-corpus-json
just curl-monitor-histogram-production-image
```

Swagger: `just swagger`. Testes: `just test`.
