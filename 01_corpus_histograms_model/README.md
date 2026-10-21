# Lição 01 — Corpus, histogramas e modelo de tons de cinza

## Objetivo

- Relembrar o que o **programa base** (raiz do repositório) já faz com BentoML.
- Acrescentar um **corpus de treino** offline e rotas de monitoramento do corpus.
- Trocar o cinza «inline» por um **modelo BentoML picklable** (ainda Pillow
  `convert("L")` — **sem pesos neurais**).
- Árvore **autocontida**: cópia independente do serviço base.

## Comparação com a base

### O que o programa base faz (antes de abrir esta pasta)

Na **raiz** do repositório há um serviço mínimo de processamento de imagens. A
ideia pedagógica da base é: você escreve métodos Python com *anotações de tipo*;
o BentoML lê essas anotações e monta HTTP, validação e OpenAPI **sem** você
escrever rotas Flask/FastAPI à mão.

Comportamento da base:

1. Sobe com `just serve` (BentoML serve a classe `ImageProcessor`).
2. Aceita `POST` multipart com uma imagem.
3. Devolve outra imagem (PNG) após um filtro Pillow.
4. Três operações apenas: desfoque, tons de cinza, redimensionamento.

Não há corpus, não há estatísticas em disco, não há modelo salvo no armazém
BentoML: o cinza é uma linha `image.convert("L")` dentro do handler.

### Recursos BentoML — antes (base) versus depois (esta lição)

| Recurso BentoML | Base (raiz) | Esta lição |
| :--- | :--- | :--- |
| `@bentoml.service` | Sim — declara `ImageProcessor` | Sim — igual |
| `@bentoml.api` + tipos (`ImageInput`, `Positive`) | Sim — gera `POST` a partir das assinaturas | Sim — iguais + rotas novas |
| Rotas `/inference-{blur,grayscale,resize}` | Sim | Sim |
| `bentoml serve service:ImageProcessor` | Sim | Sim |
| OpenAPI / Swagger automático | Sim | Sim |
| `bentoml.picklable_model` (salvar / carregar artefato) | **Não** | **Sim** — cinza vira modelo versionado |
| Rotas `/monitor-*` (relatórios) | **Não** | **Sim** — só corpus |
| Pipeline offline de features / stats | **Não** | **Sim** — fora do HTTP |

Em uma frase: a base ensina **API por anotações**; esta lição acrescenta
**modelo empacotado** e **monitoramento do corpus**, sem abandonar os três
filtros de inferência.

### Trecho decisivo no `service.py`

**AS-IS (base)** — cinza direto, sem modelo:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return image.convert("L")
```

**TO-BE (esta lição)** — carrega o modelo no arranque; acrescenta relatórios:

```python
def __init__(self) -> None:
    self._grayscale_model = load_grayscale_model()  # picklable_model:latest

@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return self._grayscale_model(image)

@bentoml.api(route="/monitor-histogram-corpus-json")
def monitor_histogram_corpus_json(self, channel: str = "L", bins: Positive = 256) -> dict:
    return report_histogram_json(channel=channel, bins=bins)
# + /monitor-histogram-corpus-csv  e  /monitor-histogram-corpus-image
```

O pipeline offline (sem endpoint) alimenta esses relatórios:

```text
samples/train_*  →  image_extract  →  features/*.json
                 →  corpus_stats   →  corpus_stats.json
                 →  corpus_report  →  respostas /monitor-histogram-corpus-*
```

Antes de servir: `just save-grayscale-model` grava o artefato com
`picklable_model.save_model` (ver `grayscale_model.py`).

| Rotas | Base | Esta lição |
| :--- | :---: | :---: |
| `/inference-blur` | sim | sim |
| `/inference-grayscale` | sim (inline) | sim (modelo) |
| `/inference-resize` | sim | sim |
| `/monitor-histogram-corpus-{json,csv,image}` | não | sim |

## Utilização

### Características extraídas e registradas das imagens de treino

Cumpre observar: o que se extrai por imagem **não** é exposto por HTTP
diretamente. A camada 1 (`image_extract.py`, receita `just extract-features`)
percorre `samples/train_*`, abre cada arquivo com Pillow, calcula um dicionário
de características e **registra-o em disco** como `features/<stem>.json`
(ex.: `train_001.jpg` → `features/train_001.json`). A camada 2
(`corpus_stats.py`) lê esses JSON — sem reabrir as imagens — e produz
`corpus_stats.json`, que as rotas `/monitor-histogram-corpus-*` reportam.

#### O que se calcula por imagem

| Campo | Tipo | Significado |
| :--- | :--- | :--- |
| `bins` | inteiro | Resolução dos histogramas; padrão **256** (`DEFAULT_BINS`). |
| `luminance_mean` | flutuante | Média ponderada dos níveis do canal **L**. |
| `histograms` | objeto | Contagens `"L"`, `"R"`, `"G"`, `"B"`. |
| `source` | cadeia | Caminho da imagem de origem (barra `/`). |

Não se registram largura/altura, EXIF, hashes nem embutidos neurais. O objeto
didático é a **distribuição de intensidade** por canal.

#### Canais

| Canal | Origem Pillow | Interpretação |
| :--- | :--- | :--- |
| **L** | `image.convert("L")` | Luminância / tons de cinza. |
| **R** | `convert("RGB").getchannel(0)` | Vermelho. |
| **G** | `convert("RGB").getchannel(1)` | Verde. |
| **B** | `convert("RGB").getchannel(2)` | Azul. |

O histograma de um canal é `Image.histogram()` sobre esse mapa, eventualmente
reagrupado com `rebin_counts` se `bins` ≠ 256.

#### `luminance_mean`

Deriva do histograma de **L** (não de uma passagem separada pelos píxeis):

```text
luminance_mean = (Σ i · counts[i]) / (Σ counts[i])
```

#### Forma do JSON por imagem (esqueleto)

```json
{
  "bins": 256,
  "luminance_mean": 112.18537109375,
  "histograms": {
    "L": [ /* 256 inteiros; soma = nº de píxeis */ ],
    "R": [ /* idem */ ],
    "G": [ /* idem */ ],
    "B": [ /* idem */ ]
  },
  "source": "…/samples/train_001.jpg"
}
```

A **CDF não** é gravada neste arquivo: só no agregado `corpus_stats.json`.

#### O que a agregação acrescenta (ainda offline)

`just build-corpus-stats` exige ≥ **50** arquivos em `features/`. Soma contagens
bin a bin; sobre os `luminance_mean` calcula brilho do corpus:

| Campo em `corpus_stats.json` | Origem |
| :--- | :--- |
| `n_images` | Número de JSON em `features/`. |
| `brightness.mean` / `p50` / `p95` | Média e percentis dos `luminance_mean`. |
| `histograms.luminance` / `r` / `g` / `b` | Contagens somadas + `cdf` (último valor = **1,0**). |

#### Onde está o código de extração

Nesta pasta da lição (não na raiz do repositório):

| Arquivo | Papel |
| :--- | :--- |
| `image_extract.py` | `extract_image_features`, `save_image_features`. |
| `scripts/extract_image_features.py` | CLI de `just extract-features` (só `train_*`). |
| `histogram.py` | `compute_histogram`, `rebin_counts`. |
| `grayscale_model.py` | `save_model` / `load_model` picklable. |

Leia primeiro `save_image_features` em `image_extract.py`.

#### Extrair dados de uma imagem sua

O lote do corpus exige `train_*`. Para **uma** foto qualquer:

```bash
cd /home/lugatj/code/research/bentoML-processamento-imagens/01_corpus_histograms_model

uv run --no-active python -c "
from pathlib import Path
from image_extract import save_image_features

caminho = Path('samples/cesar-fachada-1.webp')  # troque pela sua imagem
print('gravado:', save_image_features(caminho))
"
```

Inspecionar:

```bash
uv run --no-active python -c "
import json
from pathlib import Path
d = json.loads(Path('features/cesar-fachada-1.json').read_text())
print(d['bins'], d['luminance_mean'], list(d['histograms']), sum(d['histograms']['L']))
"
```

Um JSON avulso **não** entra sozinho no HTTP: as rotas leem `corpus_stats.json`.
Para incluir a imagem no agregado, coloque-a como `samples/train_NNN.*` e rode
de novo `just extract-features` e `just build-corpus-stats`.

### Conceitos mínimos (resumo)

| Canal | Significado |
| :--- | :--- |
| **L** | Luminância — padrão dos relatórios |
| **R** / **G** / **B** | Componentes RGB |

Porta do `just serve`: **3333**.

### Preparação

```bash
cd /home/lugatj/code/research/bentoML-processamento-imagens/01_corpus_histograms_model
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
just curl-monitor-histogram-corpus-json
just curl-monitor-histogram-corpus-csv
just curl-monitor-histogram-corpus-image
just curl-inference-grayscale samples/cesar-fachada-1.webp
just curl-inference-blur samples/cesar-fachada-1.webp
just curl-inference-resize samples/cesar-fachada-1.webp
```

Swagger: `just swagger`. Testes: `just test`.

### Atividade assíncrona

Escolha **três** fotografias suas (ou capturas do telemóvel). Para cada uma:

1. Extraia features com `save_image_features` e anote `luminance_mean`.
2. Sem incluir essas fotos no corpus, rode `just serve` e compare
   `just curl-monitor-histogram-corpus-json` (só o corpus Picsum) com os três
   valores individuais que anotou.
3. Entregue um parágrafo: as suas fotos estão mais claras, mais escuras ou
   semelhantes ao corpus? Em que canal (L vs R/G/B) a diferença é mais óbvia?
