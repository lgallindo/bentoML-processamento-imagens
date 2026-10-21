# Lição 01 — Corpus, histogramas e modelo de tons de cinza

## Objectivo

- Compreender um **corpus de treino** offline (extração → agregação → relatório).
- Servir estatísticas agregadas do corpus por HTTP (`/monitor-histogram-corpus-*`).
- Empacotar `/inference-grayscale` como **modelo BentoML picklable** (Pillow `convert("L")`).
- Árvore **autocontida**: cópia independente do serviço base (raiz); **sem pesos neurais**.

## Comparação com a base

O serviço base (raiz) expõe apenas três filtros de inferência: desfoque, cinza e
redimensionamento. O cinza é Pillow inline; **não** há corpus nem rotas de monitorização.

**AS-IS (base)** — cinza directo:

```python
@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return image.convert("L")
```

**TO-BE (esta lição)** — modelo carregado no arranque; relatórios do corpus:

```python
def __init__(self) -> None:
    self._grayscale_model = load_grayscale_model()

@bentoml.api(route="/inference-grayscale")
def inference_grayscale(self, image: ImageInput) -> PILImage:
    return self._grayscale_model(image)

@bentoml.api(route="/monitor-histogram-corpus-json")
def monitor_histogram_corpus_json(self, channel: str = "L", bins: Positive = 256) -> dict:
    return report_histogram_json(channel=channel, bins=bins)
# + /monitor-histogram-corpus-csv  e  /monitor-histogram-corpus-image
```

Pipeline offline novo (sem endpoint): `image_extract` → `corpus_stats` →
`corpus_report` lê `corpus_stats.json`.

| Rotas | Base | Esta lição |
| :--- | :---: | :---: |
| `/inference-blur` | sim | sim |
| `/inference-grayscale` | sim (inline) | sim (modelo) |
| `/inference-resize` | sim | sim |
| `/monitor-histogram-corpus-{json,csv,image}` | não | sim |

## Utilização

### Características extraídas e registadas das imagens de treino

Cumpre observar que, nesta lição, **nada** do que se extrai por imagem é exposto
por HTTP directamente. A camada 1 (`image_extract.py`, receita
`just extract-features`) percorre `samples/train_*`, abre cada ficheiro com
Pillow, calcula um dicionário de características e **regista-o em disco** como
`features/<stem>.json` (por exemplo `train_001.jpg` → `features/train_001.json`).
Só depois a camada 2 (`corpus_stats.py`) lê esses JSON — sem reabrir as imagens —
e produz `corpus_stats.json`, que as rotas `/monitor-histogram-corpus-*` reportam.

#### O que se calcula por imagem

Para cada `train_*`, o payload gravado contém exactamente estes campos:

| Campo | Tipo | Significado |
| :--- | :--- | :--- |
| `bins` | inteiro | Resolução dos histogramas; predefinição **256** (`DEFAULT_BINS`). |
| `luminance_mean` | flutuante | Média ponderada dos níveis do canal **L** (ver abaixo). |
| `histograms` | objecto | Quatro listas de contagens: chaves `"L"`, `"R"`, `"G"`, `"B"`. |
| `source` | cadeia | Caminho da imagem de origem (barra `/`), para auditoria. |

Não se registam: largura/altura, formato de ficheiro, EXIF, hashes, embutidos
neurais, nem estatísticas de textura (GLCM, etc.). O objecto didáctico é a
**distribuição de intensidade** por canal.

#### Canais

Cada histograma parte de um mapa de intensidade em modo `L` do Pillow (valores
inteiros tipicamente **0…255**):

| Canal | Origem Pillow | Interpretação |
| :--- | :--- | :--- |
| **L** | `image.convert("L")` | Luminância / tons de cinza (fórmula de conversão do Pillow). |
| **R** | `convert("RGB").getchannel(0)` | Componente vermelha. |
| **G** | `convert("RGB").getchannel(1)` | Componente verde. |
| **B** | `convert("RGB").getchannel(2)` | Componente azul. |

Assim, mesmo uma imagem WebP ou JPEG acaba normalizada a RGB (ou L) antes da
contagem. O histograma de um canal é a lista devolvida por
`Image.histogram()` sobre esse mapa, eventualmente **reagrupada** se `bins` ≠ 256
(`rebin_counts`): o índice `i` conta quantos píxeis caem no nível (ou no grupo
de níveis) correspondente.

#### `luminance_mean`

Não é a média aritmética dos píxeis lida à parte: deriva do histograma de **L**.
Se `counts[i]` é o número de píxeis no nível `i` (com `bins` níveis),

```text
luminance_mean = (Σ i · counts[i]) / (Σ counts[i])
```

isto é, a esperança do nível de luminância sob a distribuição empírica da
imagem. Com 256 bins, coincide com a média clássica dos valores 0…255 do canal L.

#### Forma do JSON por imagem (esqueleto)

```json
{
  "bins": 256,
  "luminance_mean": 112.18537109375,
  "histograms": {
    "L": [ /* 256 inteiros ≥ 0; soma = número de píxeis */ ],
    "R": [ /* idem */ ],
    "G": [ /* idem */ ],
    "B": [ /* idem */ ]
  },
  "source": "…/samples/train_001.jpg"
}
```

A soma de cada lista de contagens iguala o número de píxeis da imagem (após a
conversão de canal). A **CDF não** é gravada neste ficheiro: só aparece no
agregado do corpus.

#### O que a agregação acrescenta (ainda offline)

`just build-corpus-stats` exige pelo menos **50** ficheiros em `features/`. Para
cada canal, **soma** as contagens bin a bin; sobre a lista de
`luminance_mean` por imagem calcula brilho do corpus:

| Campo em `corpus_stats.json` | Origem |
| :--- | :--- |
| `n_images` | Número de JSON em `features/`. |
| `brightness.mean` | Média dos `luminance_mean` por imagem. |
| `brightness.p50` / `p95` | Percentis 50 e 95 dessa mesma lista (ordenada). |
| `histograms.luminance` / `r` / `g` / `b` | Contagens somadas + `cdf` normalizada (último valor = **1,0**). |

As chaves do agregado usam nomes longos (`luminance`, `r`, `g`, `b`); as rotas
HTTP aceitam o canal curto `L`/`R`/`G`/`B` e mapeiam-no de volta. Em suma: o que
se **extrai e regista** por imagem de treino é brilho médio de L mais quatro
histogramas de intensidade; o que se **serve** ao cliente é só o resumo
agregado desse registo.

#### Onde está o código de extracção

Abra, nesta pasta da lição (não na raiz do repositório):

| Ficheiro | Papel |
| :--- | :--- |
| `image_extract.py` | Biblioteca: `extract_image_features`, `save_image_features`. |
| `scripts/extract_image_features.py` | CLI da receita `just extract-features` (só `samples/train_*`). |
| `histogram.py` | `compute_histogram`, `rebin_counts`, canais L/R/G/B. |

O ponto de entrada que o estudante deve ler primeiro é
`save_image_features` em `image_extract.py`: abre o ficheiro, chama
`extract_image_features`, acrescenta `source` e grava `features/<stem>.json`.

#### Extrair dados de uma imagem sua (aleatória)

O lote do corpus exige nomes `train_*`. Para **uma** fotografia ou captura
qualquer (JPEG, PNG, WebP, …), use a mesma função de biblioteca, apontando
para o caminho do ficheiro. Na raiz **desta** lição:

```bash
cd /home/lugatj/code/research/bentoML-processamento-imagens/01_corpus_histograms_model

# Coloque a sua imagem onde preferir, por exemplo:
#   samples/minha_foto.jpg
# ou um caminho absoluto fora de samples/

uv run --no-active python -c "
from pathlib import Path
from image_extract import save_image_features

# Altere este caminho para o da sua imagem:
caminho = Path('samples/cesar-fachada-1.webp')

saida = save_image_features(caminho)
print('gravado:', saida)
"
```

O JSON aparece em `features/` com o mesmo *stem* do ficheiro (ex.:
`cesar-fachada-1.json`). Para inspeccionar:

```bash
uv run --no-active python -c "
import json
from pathlib import Path
p = Path('features/cesar-fachada-1.json')  # ajuste ao stem da sua imagem
d = json.loads(p.read_text())
print('bins', d['bins'], 'luminance_mean', d['luminance_mean'])
print('chaves histograma', list(d['histograms']))
print('soma L', sum(d['histograms']['L']))
"
```

Cumpre observar: um JSON avulso **não** entra sozinho no relatório HTTP. As
rotas `/monitor-histogram-corpus-*` leem `corpus_stats.json`. Se quiser incluir
a imagem no agregado do corpus, copie-a (ou ligue-a) como `samples/train_NNN.*`,
volte a correr `just extract-features` e `just build-corpus-stats`.

### Conceitos mínimos (resumo)

| Canal | Significado |
| :--- | :--- |
| **L** | Luminância (`convert("L")`) — predefinição dos relatórios |
| **R** / **G** / **B** | Componentes RGB |

Histograma: contagens por nível (predefinição **256** bins). **CDF**: acumulação
normalizada no agregado (último valor = **1,0**). Porta do `just serve`: **3333**.

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
