# Lição 02 — Registro de estatísticas em `/inference-grayscale`

## Objetivo

- Manter corpus e relatórios `/monitor-histogram-corpus-*` e o modelo picklable.
- **Registrar em disco** as features de cada imagem submetida a `/inference-grayscale`
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
| Relatórios do log de pedidos | não | não (só arquivos) |

## Utilização

### Onde está o código novo e o que faz

Dois locais nesta pasta (procure pelo nome do símbolo, não por pastas de outras
lições):

| Local | O que procurar |
| :--- | :--- |
| `service.py` | método `inference_grayscale` — a **chamada** ao registro. |
| `request_log.py` | função `log_grayscale_submission` — a **implementação** do registro. |

No editor: abra `service.py` e salte para `inference_grayscale`; a primeira
linha útil é `log_grayscale_submission(image)`. Em seguida abra `request_log.py`
(ou siga a importação `from request_log import log_grayscale_submission` no topo
de `service.py`).

**Gancho no serviço** (efeito lateral antes do modelo):

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    # 1) Ainda há cor: extrai L/R/G/B e grava JSON em request_features/
    log_grayscale_submission(image)
    # 2) Só depois converte a cinza via modelo picklable
    return self._grayscale_model(image)
```

**Implementação do registro** (`request_log.py`), comentada:

```python
def log_grayscale_submission(
    image: PILImage,
    features_dir: Path = REQUEST_FEATURES_DIR,  # padrão: request_features/
) -> Path:
    # Reutiliza a mesma extração do corpus (image_extract.extract_image_features)
    payload = extract_image_features(image)
    payload["logged_at"] = datetime.now(timezone.utc).isoformat()  # instante UTC
    payload["endpoint"] = "grayscale"  # marca a origem do pedido
    features_dir.mkdir(parents=True, exist_ok=True)
    # Nome único: carimbo temporal + sufixo aleatório → um arquivo por pedido
    name = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{uuid4().hex[:8]}.json"
    out = features_dir / name
    out.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return out
```

Em resumo: o JSON de pedido tem a **mesma forma** que `features/*.json` do
corpus (`bins`, `luminance_mean`, `histograms`), mais `logged_at` e `endpoint`.
Não há rota HTTP que devolva esse JSON avulso nesta lição — só o efeito em
disco.

```text
imagem a cores  →  log_grayscale_submission  →  modelo grayscale  →  PNG
                      ↓
               request_features/*.json
```

Canais **L** / **R** / **G** / **B**; padrão dos relatórios de corpus:
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
# confira novos arquivos em request_features/
just curl-monitor-histogram-corpus-json
just curl-inference-blur samples/cesar-fachada-1.webp
just curl-inference-resize samples/cesar-fachada-1.webp
```

Swagger: `just swagger`. Testes: `just test`.
