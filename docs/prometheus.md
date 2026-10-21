# Prometheus com o `/metrics` deste projeto

Uma API pode continuar respondendo `200` e, ainda assim, estar ficando mais
lenta. Observar uma chamada isolada não revela esse tipo de degradação: é
preciso medir continuamente, preservar o histórico e comparar o comportamento
atual com o padrão anterior do serviço.

O BentoML já publica contadores e histogramas HTTP em `GET /metrics`. O
Prometheus visita esse endpoint periodicamente, transforma cada coleta em uma
série temporal e oferece PromQL para calcular taxas, percentis e linhas de base.
Não é necessário alterar `service.py` nem criar um exporter adicional.

Neste tutorial, você instalará o Prometheus localmente, conectará o servidor ao
serviço deste repositório e verificará a coleta com tráfego real. Ao final,
consultará o percentil 95 do tempo de resposta e terá uma regra reproduzível
para sinalizar desvios anômalos em relação a uma janela móvel.

## 1. Instale o Prometheus

Baixe o pacote adequado ao seu sistema na
[página oficial de downloads](https://prometheus.io/download/). No Linux x86-64,
o arquivo termina em `.linux-amd64.tar.gz`. Extraia-o e coloque os dois
executáveis em um diretório do seu `PATH`:

```bash
tar xzf prometheus-*.linux-amd64.tar.gz
cd prometheus-*.linux-amd64
sudo install prometheus promtool /usr/local/bin/
prometheus --version
promtool --version
```

O Prometheus é um único servidor executável. A instalação oficial também
oferece contêineres, mas o binário local torna `127.0.0.1:3000` inequívoco e
evita diferenças de rede entre Docker, Linux, macOS e Windows.

## 2. Entenda a configuração do repositório

O arquivo [`monitoring/prometheus.yml`](../monitoring/prometheus.yml) contém um
job chamado `bentoml-imagens`:

```yaml
scrape_configs:
  - job_name: bentoml-imagens
    metrics_path: /metrics
    static_configs:
      - targets:
          - 127.0.0.1:3000
```

A cada cinco segundos, o Prometheus faz `GET
http://127.0.0.1:3000/metrics`, interpreta o texto retornado e grava uma nova
amostra de cada série temporal. `127.0.0.1` funciona porque, neste tutorial, os
dois processos rodam diretamente na mesma máquina. Em produção, troque o target
pelo nome DNS e pela porta em que o serviço é alcançável pelo Prometheus.

Valide os arquivos antes de subir qualquer processo:

```bash
promtool check config monitoring/prometheus.yml
promtool check rules monitoring/bentoml.rules.yml
```

Os dois comandos devem terminar com `SUCCESS`.

## 3. Suba os dois servidores

Abra dois terminais na raiz do repositório.

No terminal 1, inicie o BentoML:

```bash
just sync
just serve
```

Confira primeiro a origem das métricas:

```bash
curl --fail http://127.0.0.1:3000/metrics
```

No terminal 2, inicie o Prometheus. O diretório em `/tmp` mantém o banco de
dados gerado pela aula fora do repositório:

```bash
prometheus \
  --config.file=monitoring/prometheus.yml \
  --storage.tsdb.path=/tmp/bentoml-imagens-prometheus
```

Acesse <http://127.0.0.1:9090/targets>. O target `bentoml-imagens` deve aparecer
como `UP`. A expressão abaixo faz a mesma verificação pela API do Prometheus:

```bash
curl --get --silent --show-error --fail \
  --data-urlencode 'query=up{job="bentoml-imagens"}' \
  http://127.0.0.1:9090/api/v1/query
```

No resultado JSON, `status` deve ser `success` e o valor da série deve ser `1`.
Se aparecer `DOWN`, confirme que o BentoML continua rodando, que sua porta é
3000 e que `curl http://127.0.0.1:3000/metrics` responde.

## 4. Gere tráfego e consulte a latência

Em um terceiro terminal, envie algumas imagens. Escolha um arquivo que exista
diretamente em `samples/`; se você já executou a análise que cria clusters, use
um arquivo dentro de `samples/clustered/`:

```bash
IMAGE=$(find samples -type f \( -name '*.jpg' -o -name '*.webp' \) | head -1)

for i in $(seq 1 10); do
  just curl-inference-resize "$IMAGE" /tmp/resized.png 256 256
done
```

Espere pelo menos cinco segundos para ocorrer uma nova coleta. Na interface em
<http://127.0.0.1:9090/query>, consulte a taxa de requisições por endpoint:

```promql
sum by (endpoint) (rate(bentoml_service_request_total[1m]))
```

Consulte o percentil 95 do tempo de resposta:

```promql
histogram_quantile(
  0.95,
  sum by (le, endpoint) (
    rate(bentoml_service_request_duration_seconds_bucket{
      endpoint=~"/(blur|grayscale|resize)"
    }[1m])
  )
)
```

O resultado está em segundos. `histogram_quantile` estima o p95 a partir dos
buckets cumulativos do histograma; ele não seleciona literalmente a 95ª
requisição.

## 5. Detecte uma anomalia de tempo de resposta

[`monitoring/bentoml.rules.yml`](../monitoring/bentoml.rules.yml) grava o p95 de
um minuto como `bentoml:http_request_duration_seconds:p95_1m`. Depois compara o
valor atual com a média móvel de 30 minutos. O alerta
`BentoMLResponseTimeAnomaly` fica pendente quando o p95 ultrapassa a média em
três desvios-padrão e dispara se a condição durar um minuto.

Consulte o sinal calculado:

```promql
bentoml:http_request_duration_seconds:p95_1m
```

E veja o estado do alerta em <http://127.0.0.1:9090/alerts> ou consulte:

```promql
ALERTS{alertname="BentoMLResponseTimeAnomaly"}
```

O alerta precisa de histórico. Nos primeiros minutos, poucos pontos e desvio
padrão zero tornam a linha de base frágil; deixe a carga normal rodar antes de
interpretá-lo. Três desvios-padrão são um ponto de partida didático, não um
limite universal. Ajuste a janela, o multiplicador e o `for` depois de observar
o padrão real do serviço. Uma distribuição sazonal ou multimodal exige um
modelo mais cuidadoso do que esta linha de base simples.

## 6. Encerre e limpe

Pressione `Ctrl+C` nos terminais do Prometheus e do BentoML. Os dados desta aula
ficam em `/tmp/bentoml-imagens-prometheus`; você pode apagá-los quando não
precisar mais do histórico.

## Referências

- [Métricas e integração Prometheus do BentoML](https://docs.bentoml.org/en/latest/build-with-bentoml/observability/metrics.html)
- [Primeiros passos com Prometheus](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [Instalação do Prometheus](https://prometheus.io/docs/prometheus/latest/installation/)
