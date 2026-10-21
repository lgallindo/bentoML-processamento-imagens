# Lição 02 — Registo de estatísticas em `/inference-grayscale`

## Objectivo

- Manter corpus e relatórios `/monitor-histogram-corpus-*` e o modelo picklable.
- **Registar em disco** as features de cada imagem submetida a `/inference-grayscale`
  (antes da conversão a cinza), em `request_features/`.
- Compreender por que o log ocorre **antes** do cinza (canais R/G/B ainda existem).
- Árvore **autocontida**: cópia independente do serviço base (raiz); **sem pesos neurais**.

## Comparação com a base

O serviço base só devolve a imagem filtrada; **não** grava features de pedidos.

**AS-IS (base)** — cinza sem efeitos laterais:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return image.convert("L")
```

**TO-BE (esta lição)** — log offline, depois modelo:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    log_grayscale_submission(image)   # → request_features/*.json
    return self._grayscale_model(image)
```

O módulo `request_log` escreve JSON com a mesma forma do corpus (`luminance_mean`,
histogramas L/R/G/B), mais `logged_at`. Nesta lição o log **não** tem API de
relatório de production.

| Rotas | Base | Esta lição |
| :--- | :---: | :---: |
| `/inference-{blur,grayscale,resize}` | sim | sim (grayscale com log) |
| `/monitor-histogram-corpus-{json,csv,image}` | não | sim |
| Relatórios do log de pedidos | não | não (só ficheiros) |

## Utilização

### Conceitos mínimos

```text
imagem a cores  →  log_grayscale_submission  →  modelo grayscale  →  PNG
                      ↓
               request_features/*.json
```

Canais **L** / **R** / **G** / **B**; predefinição dos relatórios de corpus:
`channel="L"`, `bins=256`. Porta: **3333**.

### Preparação

```bash
cd /home/lugatj/code/research/bentoML-processamento-imagens/02_grayscale_request_logging
just sync
just download-samples
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
just curl-inference-grayscale samples/cesar-fachada-1.webp
# confira novos ficheiros em request_features/
just curl-monitor-histogram-corpus-json
just curl-inference-blur samples/cesar-fachada-1.webp
just curl-inference-resize samples/cesar-fachada-1.webp
```

Swagger: `just swagger`. Testes: `just test`.
