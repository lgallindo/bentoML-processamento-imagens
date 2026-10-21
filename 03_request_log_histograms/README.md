# Lição 03 — Histogramas do log de pedidos e exercitador

## Objetivo

- **Finalidade pedagógica (MLOps):** descobrir se as imagens que chegam em
  *production* (pedidos reais a `/inference-grayscale`) **diferem** das imagens
  usadas no *training* (corpus `train_*`), olhando para as mesmas estatísticas
  de canal — e compreender **por que** essa vigilância importa.
- Agregar `request_features/` em `request_stats.json` e **reportar** histogramas
  de production (`/monitor-histogram-production-*`), gêmeos dos do corpus, para
  que a comparação visual/numérica seja possível lado a lado.
- Separar **download offline** do exercitador (`bentoml-exer-*`) da **submissão
  cronometrada** a `/inference-grayscale`.
- Árvore **autocontida**: cópia independente do serviço base (raiz); **sem pesos neurais**.

## Comparação com a base

O serviço base não registra pedidos nem expõe monitoramento. Esta lição acrescenta
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

### Finalidade: treino versus produção

Em sistemas de visão (e, por analogia, em qualquer modelo servido), o
desempenho no laboratório só se mantém se os dados de **produção** se
parecerem com os de **treino**. Quando a distribuição muda — câmeras
diferentes, iluminação nocturna, compressão agressiva, outro domínio de
conteúdo — o serviço continua a responder HTTP 200, mas a qualidade da
transformação (ou, em outros projetos, da predição) **degrada em silêncio**.

Esta lição não treina uma rede: usa histogramas e CDF de L/R/G/B como
**proxy observável** dessa distribuição. O corpus (`/monitor-histogram-corpus-*`)
é a referência do que o sistema “viu” no treino; o log agregado
(`/monitor-histogram-production-*`) é o que a API está a receber agora. Ao
colocar os dois relatórios no mesmo formato, o estudante pode:

1. Exercitar o serviço com imagens **outras** que as do corpus (`bentoml-exer-*`).
2. Reconstruir `request_stats.json` e comparar forma das curvas (picos, caudas,
   brilho) com `corpus_stats.json`.
3. Formular a pergunta de monitoramento: *a produção ainda se parece com o
   treino?* — base da detecção de *data drift* / *covariate shift*, que mais
   tarde se formaliza com testes estatísticos sobre as mesmas CDF.

Por que isto é importante na prática:

- **Falsos negativos de qualidade:** métricas de *uptime* e latência não
  detectam imagens “estranhas”; só métricas de **dados** o fazem.
- **Decisão de re-treino ou de alerta:** se production diverge de forma
  estável, há de se investigar a origem (cliente, pipeline, domínio) antes de
  culpar o modelo.
- **Separação de responsabilidades:** inferência continua a servir o cliente;
  monitoramento observa o tráfego sem misturar os conjuntos de arquivos
  (`train_*` versus `exer_*`).

### Conceitos mínimos

```text
samples/train_*.jpg            seeds  bentoml-edu-N    (corpus)
exerciser_samples/exer_*.jpg   seeds  bentoml-exer-N   (exercitador)
```

Não misturar os dois conjuntos. Padrão: `channel="L"`, `bins=256`. Porta: **3333**.

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
