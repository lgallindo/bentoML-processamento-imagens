# Grafana para visualizar as métricas deste projeto

Este tutorial continua o roteiro de
[Prometheus com o `/metrics` deste projeto](prometheus.md). O BentoML expõe as
métricas; o Prometheus coleta e armazena as séries temporais; o Grafana consulta
o Prometheus e transforma os resultados em painéis. O Grafana não consulta
`/metrics` diretamente.

Ao final, você terá um painel com volume de requisições, p95 do tempo de
resposta e a linha de base usada para detectar anomalias.

## 1. Confirme os pré-requisitos

Conclua primeiro o tutorial do Prometheus. Em dois terminais, mantenha ativos:

```bash
# terminal 1
just serve

# terminal 2
prometheus \
  --config.file=monitoring/prometheus.yml \
  --storage.tsdb.path=/tmp/bentoml-imagens-prometheus
```

Confirme os dois lados da coleta:

```bash
curl --fail http://127.0.0.1:3000/metrics >/dev/null

curl --get --silent --show-error --fail \
  --data-urlencode 'query=up{job="bentoml-imagens"}' \
  http://127.0.0.1:9090/api/v1/query
```

O JSON da segunda chamada deve conter o valor `1`.

## 2. Instale o Grafana OSS no Debian ou Ubuntu

Cadastre o repositório APT oficial e instale a edição open source:

```bash
sudo apt-get install -y apt-transport-https wget gnupg
sudo mkdir -p /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/grafana.asc https://apt.grafana.com/gpg-full.key
sudo chmod 644 /etc/apt/keyrings/grafana.asc

echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" \
  | sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt-get update
sudo apt-get install -y grafana
```

O Grafana usa a porta 3000 por padrão, mas ela já pertence ao BentoML neste
projeto. Altere o Grafana para 4000:

```bash
sudo sed -i \
  '/^\[server\]/,/^\[/ s/^;http_port = 3000/http_port = 4000/' \
  /etc/grafana/grafana.ini
```

Confira a alteração antes de iniciar o serviço:

```bash
grep -A20 '^\[server\]' /etc/grafana/grafana.ini | grep '^http_port = 4000'
```

## 3. Provisione a conexão com o Prometheus

Em vez de criar uma conexão manual e deixá-la guardada apenas no banco local do
Grafana, instale a configuração versionada deste repositório:

```bash
sudo install -m 0644 \
  monitoring/grafana/datasources/bentoml-prometheus.yml \
  /etc/grafana/provisioning/datasources/bentoml-prometheus.yml
```

O arquivo define `http://127.0.0.1:9090` como fonte padrão. Esse endereço é
correto porque Grafana e Prometheus rodam diretamente na mesma máquina. Se eles
forem separados em hosts ou contêineres, use o endereço pelo qual o processo do
Grafana realmente alcança o Prometheus; `localhost` sempre significa o próprio
ambiente de rede do Grafana.

Agora inicie o serviço e faça-o subir automaticamente com o sistema:

```bash
sudo systemctl enable --now grafana-server
sudo systemctl restart grafana-server
sudo systemctl status grafana-server --no-pager
```

Acesse <http://127.0.0.1:4000>. No primeiro acesso, entre com usuário `admin` e
senha `admin`; o Grafana pedirá a troca da senha. Em **Connections → Data
sources**, a fonte `Prometheus — BentoML Imagens` já deve existir. Ela aparece
como não editável porque sua fonte da verdade é o YAML do repositório.

## 4. Gere tráfego para os gráficos

Em outro terminal, escolha uma imagem e envie uma requisição por segundo:

```bash
IMAGE=$(find samples -type f \( -name '*.jpg' -o -name '*.webp' \) | head -1)

for i in $(seq 1 60); do
  just curl-resize "$IMAGE" /tmp/resized.png 256 256
  sleep 1
done
```

O intervalo de coleta é de cinco segundos. Sessenta requisições dão ao gráfico
tempo suficiente para exibir vários pontos, mas ainda não constituem uma boa
linha de base para anomalias.

## 5. Monte o dashboard

Abra **Dashboards → New → New dashboard → Add visualization** e selecione a
fonte `Prometheus — BentoML Imagens`. Em cada painel, mude o editor de consulta
para **Code**, cole a PromQL indicada e clique em **Run queries**.

### Painel 1 — requisições por segundo

Use a visualização **Time series**, título `Requisições por segundo` e unidade
`requests/sec`:

```promql
sum by (endpoint) (
  rate(bentoml_service_request_total[1m])
)
```

Configure a legenda como `{{endpoint}}`. O `rate` transforma o contador
acumulado em uma taxa por segundo; por isso o gráfico continua comparável mesmo
quando o processo reinicia e o contador volta a zero.

### Painel 2 — p95 do tempo de resposta

Use **Time series**, título `Tempo de resposta p95` e unidade `seconds (s)`:

```promql
bentoml:http_request_duration_seconds:p95_1m
```

Essa série é a recording rule criada em
[`monitoring/bentoml.rules.yml`](../monitoring/bentoml.rules.yml). O Prometheus
calcula o percentil a cada ciclo de avaliação; o Grafana apenas consulta o
resultado já gravado.

### Painel 3 — valor atual versus linha de base

Crie outro **Time series** com duas consultas. A consulta A é o p95 atual:

```promql
bentoml:http_request_duration_seconds:p95_1m
```

A consulta B é o limite dinâmico de três desvios-padrão:

```promql
avg_over_time(bentoml:http_request_duration_seconds:p95_1m[30m])
+ 3 * stddev_over_time(bentoml:http_request_duration_seconds:p95_1m[30m])
```

Nomeie as legendas `p95 — {{endpoint}}` e `limite — {{endpoint}}`. O alerta do
Prometheus compara exatamente essas duas curvas e exige que a ultrapassagem dure
um minuto. O limite é uma demonstração estatística simples: ele deve ser
calibrado com tráfego real antes de uso operacional.

## 6. Veja o alerta que já pertence ao Prometheus

O arquivo de regras do projeto é avaliado pelo Prometheus, não pelo Grafana. No
Grafana, abra **Alerts & IRM → Alerting → Alert rules** e selecione a fonte do
Prometheus para consultar as regras fornecidas por ela. Regras gerenciadas pela
fonte aparecem como somente leitura: alterações devem ser feitas em
`monitoring/bentoml.rules.yml` e recarregadas no Prometheus.

Também é possível criar um painel **State timeline** usando:

```promql
ALERTS{alertname="BentoMLResponseTimeAnomaly"}
```

A série só existe enquanto o alerta está pendente ou disparado. A ausência de
resultado normalmente significa que nenhuma anomalia está ativa; não significa
que a coleta parou. Use `up{job="bentoml-imagens"}` para verificar a coleta.

## 7. Salve e verifique

Salve o dashboard como `BentoML — processamento de imagens`. Se algum painel
estiver vazio, siga esta ordem:

1. confirme que BentoML, Prometheus e Grafana estão ativos;
2. confirme que `up{job="bentoml-imagens"}` vale `1` no Prometheus;
3. amplie o intervalo do dashboard para **Last 30 minutes**;
4. gere novas requisições e aguarde uma coleta de cinco segundos;
5. confirme que o painel usa a fonte `Prometheus — BentoML Imagens`.

Após um reboot, `grafana-server` inicia pelo systemd, mas os comandos `just
serve` e `prometheus` acima rodam em primeiro plano e não são serviços
habilitados para iniciar automaticamente. Confira a origem e a coleta:

```bash
sudo systemctl is-active grafana-server
curl --fail http://127.0.0.1:3000/metrics >/dev/null
curl --get --silent --show-error --fail \
  --data-urlencode 'query=up{job="bentoml-imagens"}' \
  http://127.0.0.1:9090/api/v1/query
```

Se BentoML ou Prometheus não estiverem ativos, abra terminais na raiz do
repositório e inicie-os novamente:

```bash
# terminal 1
just serve
```

```bash
# terminal 2
prometheus \
  --config.file=monitoring/prometheus.yml \
  --storage.tsdb.path=/tmp/bentoml-imagens-prometheus
```

O Prometheus só atualiza os gráficos enquanto consegue coletar `/metrics`;
depois de reiniciar os processos, gere tráfego novamente. Como o banco de dados
do tutorial fica em `/tmp`, o reboot também pode apagar o histórico anterior.

O fluxo completo é:

```text
cliente → BentoML :3000/metrics ← Prometheus :9090 ← Grafana :4000
```

## Referências

- [Instalar Grafana no Debian ou Ubuntu](https://grafana.com/docs/grafana/latest/setup-grafana/installation/debian/)
- [Configurar uma fonte Prometheus](https://grafana.com/docs/grafana/latest/datasources/prometheus/configure/)
- [Provisionar fontes de dados com YAML](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Alertas Prometheus no Grafana](https://grafana.com/docs/grafana/latest/datasources/prometheus/alerting/)
