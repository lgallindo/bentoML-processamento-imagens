# Dados de exemplo para explorar PromQL

[Voltar à aula 015](README.md). Pré-req: [aula 010](../010_prometheus_promql/README.md).

Vamos gerar uma sequência de métricas sintéticas e deixá-la disponível em
`/metrics`. O Prometheus fará a coleta e armazenará as amostras para consultas.
Você poderá observar uma fase estável, uma fase lenta e uma recuperação sem
depender da velocidade do seu computador para produzir a mudança.

Estes dados são **sintéticos**: os tempos de resposta são construídos pelo
gerador. Não são medições do BentoML nem evidência de desempenho de um modelo.
As portas **8010** / **9100** / **8515** são **auxiliares** desta demo; o
trio canônico do curso continua **3000** / **9090** / **4000**
([`docs/ports.md`](../docs/ports.md)).

## 1. Gere os dados

Depois de instalar Prometheus e `promtool` pelo
[pré-requisito](../docs/prometheus.md), abra um terminal na pasta desta aula:

```bash
cd 015_prometheus_histcdf_streamlit
just sync
uv run --no-active python scripts/serve_sample_metrics.py
```

O processo fica ativo em `http://127.0.0.1:8010/metrics`. Em outro terminal,
consulte uma amostra do texto:

```bash
curl --fail http://127.0.0.1:8010/metrics
```

Cada segundo decorrido acrescenta observações fictícias aos contadores. A
quantidade não depende de quantas vezes você faz `curl` ou de quantos scrapes
o Prometheus realiza. Os contadores reiniciam quando o gerador reinicia.

| Endpoint | Requisições geradas por segundo | Durações na fase estável |
|---|---:|---|
| `/inference-grayscale` | 20 | Entre 0,004 e 0,080 s |
| `/inference-blur` | 10 | Entre 0,008 e 0,080 s |
| `/inference-resize` | 5 | Entre 0,004 e 0,080 s |

O ciclo repete a cada seis minutos, contados desde a partida do gerador:

| Tempo dentro do ciclo | Fase | Efeito sobre as observações novas |
|---|---|---|
| 0–120 s | 0 — estável | Durações da tabela acima |
| 120–240 s | 1 — lenta | Cada duração é multiplicada por 10 |
| 240–360 s | 2 — recuperação | Voltam as durações da fase estável |

A taxa de requisições permanece constante nas três fases. Assim você muda a
latência mantendo o volume controlado. A métrica `aula004_demo_phase` informa
a fase atual, e `aula004_demo_elapsed_seconds`, o tempo desde a partida.

## 2. Carregue as amostras no Prometheus

O arquivo [`prometheus-demo.yml`](prometheus-demo.yml) aponta o coletor para
o gerador em `:8010`, a cada cinco segundos. Ele identifica as séries com
`job="bentoml-imagens"` e `source="synthetic"`. A carga ocorre por coleta HTTP,
como no serviço real. Um arquivo JSON de fixture do painel não é importado
como histórico de séries temporais.

Em um segundo terminal, também nesta pasta:

```bash
promtool check config prometheus-demo.yml
prometheus \
  --config.file=prometheus-demo.yml \
  --web.listen-address=127.0.0.1:9100 \
  --storage.tsdb.path=/tmp/aula004-prometheus
```

Esta instância usa porta e diretório de dados próprios. O Prometheus do
pré-requisito pode continuar em `:9090` observando o BentoML real. O arquivo
de demonstração também carrega as regras de `../monitoring/bentoml.rules.yml`.

Abra <http://127.0.0.1:9100/targets>: o target deve aparecer como `UP`.
Em <http://127.0.0.1:9100/query>, consulte:

```promql
up{job="bentoml-imagens", source="synthetic"}
```

Espere uma coleta bem-sucedida: o valor esperado é **1**. Para conferir pela API:

```bash
curl --get --silent --show-error --fail \
  --data-urlencode 'query=up{job="bentoml-imagens",source="synthetic"}' \
  http://127.0.0.1:9100/api/v1/query
```

O resultado deve conter `"status":"success"` e uma série com valor `"1"`.
Isso confirma a coleta do gerador. Os dados anteriores à partida desta
instância não aparecem retroativamente: deixe os dois processos rodando para
formar o histórico.

## 3. Explore taxas, buckets e percentis

Use a aba de tabela para o valor atual e o gráfico para os últimos 15 minutos.
Aguarde pelo menos duas coletas para `rate`; após um minuto haverá uma janela
inteira de amostras. Ao cruzar fases, a janela contém uma mistura das duas.

```promql
sum by (endpoint) (
  rate(bentoml_service_request_total{
    job="bentoml-imagens", source="synthetic"
  }[1m])
)
```

Com coletas regulares, espere aproximadamente **20, 10 e 5 req/s**. A taxa total
é aproximadamente **35 req/s**. O arredondamento do relógio para segundos e
os limites das coletas podem produzir pequenas variações na estimativa.

```promql
histogram_quantile(
  0.95,
  sum by (le, endpoint) (
    rate(bentoml_service_request_duration_seconds_bucket{
      job="bentoml-imagens", source="synthetic"
    }[1m])
  )
)
```

Para grayscale, uma janela inteiramente estável tem p95 estimado de
**0,075 s**; inteiramente lenta, **0,75 s**. No caso estável, o rank 19 de
20 cai entre 18 observações até 0,05 s e 20 até 0,1 s:

```text
0,05 + (0,1 − 0,05) × (19 − 18)/(20 − 18) = 0,075 s
```

Na fase lenta, essa interpolação ocorre entre 0,5 e 1,0 s. As durações geradas
não incluem exatamente 0,075 ou 0,75 s: esses valores são estimativas obtidas
dos buckets. Aguarde a janela de um minuto passar completamente pela transição
antes de comparar com esses valores.

Para mostrar a latência média por requisição na mesma janela:

```promql
sum by (endpoint) (
  rate(bentoml_service_request_duration_seconds_sum{
    job="bentoml-imagens", source="synthetic"
  }[1m])
)
/
sum by (endpoint) (
  rate(bentoml_service_request_duration_seconds_count{
    job="bentoml-imagens", source="synthetic"
  }[1m])
)
```

Grayscale produz média **0,0286 s** na fase estável e **0,286 s** na fase lenta.
A unidade é segundos por requisição, pois dividimos segundos acumulados por
contagem de requisições. Registre por que a média difere do p95.

## 4. Compare com o painel da aula

Em um terceiro terminal nesta pasta:

```bash
just app
```

Abra <http://127.0.0.1:8515>, escolha o modo conectado e informe
`http://127.0.0.1:9100` como URL do Prometheus. Selecione grayscale e atualize.
O painel compara Python e PromQL sobre os **buckets acumulados desde a partida
do gerador**. Já a consulta com `rate` acima descreve a janela recente. Depois
de uma fase lenta, o acumulado ainda contém suas observações durante a recuperação.

O ambiente carrega a recording rule de p95 e o alerta da raiz. Consulte:

```promql
bentoml:http_request_duration_seconds:p95_1m
```

Essas séries são agregadas por endpoint; o label `source` não permanece na
regra existente. Esta instância coleta somente o gerador sintético. A média
móvel de 30 minutos começa com o histórico disponível, e o ciclo se repete
várias vezes dentro dela. O roteiro garante a mudança de distribuição;
**não garante disparo do alerta de três desvios padrão**. Compare as curvas
e explique o resultado observado sem mudar o limiar para forçar um disparo.

## 5. Entrega curta

Salve as consultas, um gráfico da taxa e outro do p95. Anote a origem sintética,
o endpoint, a janela de um minuto e os instantes das fases. Responda:

1. Por que a taxa permanece praticamente constante quando o p95 sobe?
2. Por que o p95 leva cerca de uma janela para refletir só a fase nova?
3. Por que o p95 acumulado do painel pode continuar alto na recuperação?
4. Que dados adicionais você coletaria antes de concluir a causa de uma lentidão real?

Respostas esperadas: a construção mantém requisições por segundo e altera
durações; uma janela móvel mistura fases enquanto cruza a fronteira; o
histograma acumulado conserva o passado; uma causa real exigiria evidências
como carga, tamanho dos pedidos, uso de recursos e alterações do serviço.

Encerre os processos com `Ctrl+C`. O diretório `/tmp/aula004-prometheus`
preserva o histórico enquanto existir; reiniciar somente o gerador reinicia
os contadores e a fase, mas não apaga o histórico armazenado pelo Prometheus.

## Referências

- [Formato de exposição de métricas](https://prometheus.io/docs/instrumenting/exposition_formats/): estrutura dos contadores e histogramas usados pelo gerador.
- [Configuração do Prometheus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/): jobs, labels e intervalos de coleta.
