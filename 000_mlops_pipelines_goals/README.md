# Lição 000 — Pipelines de MLOps e objetivos de monitoramento

## Objetivo

- Ver o desenho das **pipelines de MLOps** (treinamento → inferência →
  monitoramento) e lembrar que a **máquina virtual / runtime de inferência é
  gerida pelo BentoML**.
- Fixar a **arquitetura-alvo de observabilidade**: BentoML → Prometheus →
  Grafana.
- Guardar três **objetivos finais** de monitoramento do servidor:

  1. **Saúde do servidor** — o serviço responde, a taxa de erro e a latência
     ficam em faixa aceitável (métricas no caminho BentoML → Prometheus →
     Grafana).
  2. **Drift de dados** — a distribuição dos pedidos (ou das features) se
     afasta do corpus de referência.
  3. **Detecção de anomalias** — uma janela de métrica foge da linha de base
     (por exemplo média ± k desvios-padrão no p95).

## Comparação com a base

### O que o programa base faz

Na **raiz** do repositório há um serviço BentoML de filtros de **imagem**. Ele
expõe rotas de inferência e o endpoint `/metrics` que o Prometheus pode coletar.

### O que esta lição acrescenta

Aqui não há servidor novo nem app interativo. É o momento de **mostrar** o
mapa: as camadas de MLOps, quem gere o runtime (BentoML) e para onde as
métricas vão (Prometheus, depois Grafana), com os três objetivos de
monitoramento escritos de forma estável.

| Recurso | Base (raiz) | Esta lição |
| :--- | :--- | :--- |
| Entrega | serviço HTTP BentoML | handout + figuras |
| Runtime | `just serve` | — (o desenho mostra o runtime gerido pelo BentoML) |
| Observabilidade | `/metrics` pronto para scrape | figura BentoML → Prometheus → Grafana |
| Objetivos | implícitos nos docs de monitoramento | saúde, drift, anomalias nomeados |

### Trecho decisivo

```text
BentoML  →  Prometheus  →  Grafana
(expõe)     (coleta)        (mostra)
```

## Utilização

```bash
just sync
just open-diagram    # pipelines de MLOps (+ legenda BentoML)
just open-target     # BentoML → Prometheus → Grafana
```

As figuras ficam em [`illustrations/`](illustrations/). Abra o README neste
terminal ou no editor e projete as duas imagens na ordem: primeiro o mapa das
pipelines, depois a cadeia de observabilidade.

O BentoML empacota e sobe o runtime que atende o “mundo” (a máquina virtual /
contêiner da figura de pipelines). O Prometheus visita `/metrics`; o Grafana
consulta o Prometheus para painéis e alertas.

Testes (existência e tamanho das figuras + rótulos no README):

```bash
just test
```
