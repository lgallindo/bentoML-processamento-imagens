# Aula 009 — Runtime BentoML em imagem OCI

Depois do vocabulário (`001`–`002`), o serviço precisa existir como
**artefacto**: empacotado, reproduzível e alcançável na porta canónica
**3000**, com `GET /metrics` raspável — antes de consultar séries no
Prometheus (`010`).

Esta aula é a **ponte** entre o Ato 0 e o Ato I. Não ensina PromQL nem
drift.

## Objectivos

1. Empacotar o serviço com `bentoml build` (receita `just build` na raiz).
2. Produzir uma imagem **OCI** (`just containerize`) e subi-la com Docker.
3. Confirmar `http://127.0.0.1:3000/metrics` a partir do contêiner.
4. Nomear três famílias de métricas que a aula `010` irá consultar.
5. Ler o fluxo raso de CI em [`.github/workflows/bentoml-oci.yml`](../.github/workflows/bentoml-oci.yml) — **sem** editar o YAML.

## Pré-requisitos

- Docker Engine no anfitrião (para `containerize` / `docker run`).
- `uv` e as dependências da raiz (`just sync`).
- Ficheiros da raiz: [`bentofile.yaml`](../bentofile.yaml),
  [`service.py`](../service.py), [`justfile`](../justfile).

## 1. Empacote o bento

Na raiz do repositório:

```bash
just sync
just build
just list
```

Anote a etiqueta (tag) do bento listada por `just list`.

## 2. Gere a imagem OCI

```bash
just containerize
```

A receita chama `bentoml containerize` sobre o bento mais recente (ou o
`tag` que passar como argumento). O resultado é uma imagem Docker/OCI
local.

## 3. Suba o runtime e prove `/metrics`

```bash
just oci-smoke
```

Ou, manualmente (substitua `IMAGE` pela etiqueta impressa):

```bash
docker run --rm -p 3000:3000 "$IMAGE"
# noutro terminal:
curl --fail --silent --show-error http://127.0.0.1:3000/metrics | head
```

Contrato de portas: BentoML permanece em **3000** ([`docs/ports.md`](../docs/ports.md)).
Grafana **não** usa 3000 neste curso.

## 4. Critério de saída da ponte

Preencha [`CHECKLIST.md`](CHECKLIST.md): três famílias (ou nomes) de
métricas visíveis em `/metrics` que a [`010_prometheus_promql`](../010_prometheus_promql/README.md)
poderá seleccionar. Exemplos típicos neste serviço: contadores de pedido,
histogramas de duração, séries auxiliares de processo — confirme no texto
exposto, não invente.

## 5. CI raso (só leitura)

Abra [`.github/workflows/bentoml-oci.yml`](../.github/workflows/bentoml-oci.yml).
Identifique o passo que executa o equivalente a `bentoml build`. Não é
preciso alterar o fluxo nem publicar em GHCR nesta aula.

## Roteiro da trilha

| | Pasta |
| :--- | :--- |
| **Anterior** | [`002_histogram_cdf_streamlit`](../002_histogram_cdf_streamlit/README.md) |
| **Seguinte** | [`010_prometheus_promql`](../010_prometheus_promql/README.md) ([`docs/prometheus.md`](../docs/prometheus.md)) |

Ordem completa: [`000_mlops_pipelines_goals`](../000_mlops_pipelines_goals/README.md).
