# Prometheus com o `/metrics` deste projeto

Mapa de portas do curso: [ports.md](ports.md) (BentoML **3000**, Prometheus
**9090**, Grafana **4000**).

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

Aprofundamento em consultas e formato de `/metrics`:
[aula 010](../010_prometheus_promql/README.md).

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

### O que o Prometheus faz com `monitoring/prometheus.yml`

Ao iniciar o processo com `--config.file=monitoring/prometheus.yml`, o
servidor **lê esse YAML uma vez na partida** (e de novo se você recarregar a
configuração). O arquivo não é um script: é um **contrato de coleta**. A partir
dele o Prometheus monta uma lista de *jobs*; cada job descreve *onde* buscar
texto no formato Prometheus e *com que frequência* fazê-lo.

Neste repositório o arquivo é deliberadamente curto:

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

rule_files:
  - bentoml.rules.yml

scrape_configs:
  - job_name: bentoml-imagens
    metrics_path: /metrics
    static_configs:
      - targets:
          - 127.0.0.1:3000
```

Leitura de cima para baixo:

1. **`global`** — padrões para todos os jobs. `scrape_interval: 5s` diz que, a
   cada cinco segundos, cada target ativo recebe um `GET` de scrape.
   `evaluation_interval: 5s` controla com que frequência as **regras**
   (recording e alertas em `bentoml.rules.yml`) são recalculadas.
2. **`rule_files`** — caminhos relativos ao diretório do arquivo de config
   (aqui, `monitoring/`). O Prometheus carrega
   [`bentoml.rules.yml`](../monitoring/bentoml.rules.yml) e passa a gravar
   séries derivadas e a avaliar alertas.
3. **`scrape_configs`** — lista de jobs. Só há um: `bentoml-imagens`.
4. **`job_name`** — vira o label `job="bentoml-imagens"` em todas as séries
   coletadas por esse bloco (além do que o próprio `/metrics` já expõe).
5. **`metrics_path: /metrics`** — caminho HTTP anexado ao host:porta do target.
   Equivale a pedir `http://127.0.0.1:3000/metrics`.
6. **`static_configs` / `targets`** — lista fixa de `host:porta`. Aqui,
   `127.0.0.1:3000` é o BentoML local (`just serve`). Em produção você
   trocaria por DNS interno ou service discovery; a sintaxe do job permanece.

A cada intervalo, o servidor faz o `GET`, interpreta o texto (`# HELP`,
`# TYPE`, amostras `nome{labels} valor`), e anexa um ponto novo a cada série
no armazenamento local (`--storage.tsdb.path`). Se o target estiver fora do ar,
a página `/targets` mostra `DOWN` e a série `up` fica em `0`.

### Sintaxe YAML (o suficiente para ler este arquivo)

YAML descreve estruturas por **indentação** (espaços, não tab). Um mapa é
`chave: valor`. Uma lista usa `-` no início do item. Strings em geral não
precisam de aspas; use aspas se houver `:` ou caracteres especiais no valor.

Blocos aninhados neste arquivo:

```text
global:                 # mapa
  scrape_interval: 5s   # pares chave/valor
scrape_configs:         # lista de mapas
  - job_name: ...       # primeiro (e único) elemento da lista
    static_configs:     # lista dentro do job
      - targets:        # um static_config
          - 127.0.0.1:3000
```

Unidades de tempo do Prometheus aceitam sufixos `s`, `m`, `h` (`5s`, `1m`,
`30m`). O nome do job e os labels devem ser estáveis: mudar `job_name` cria
séries “novas” do ponto de vista das consultas.

### Como “parsear” mentalmente (e na prática)

1. **Olho humano:** comece por `scrape_configs` → `job_name` → `targets` →
   monte a URL completa `scheme://target` + `metrics_path`.
2. **Validação:** `promtool check config` (abaixo) confirma que o YAML é
   aceito pela versão do binário.
3. **Runtime:** em `/config` na UI do Prometheus, ou
   `GET /api/v1/status/config`, você vê a configuração **efetivamente
   carregada** — útil para descobrir se a porta 9090 pertence a outra
   instância.
4. **Efeito observável:** `/targets` lista cada target com estado `UP`/`DOWN`
   e o último scrape.

Trecho essencial do job deste curso:

```yaml
scrape_configs:
  - job_name: bentoml-imagens
    metrics_path: /metrics
    static_configs:
      - targets:
          - 127.0.0.1:3000
```

### O que é o `promtool`

`promtool` é o **utilitário de linha de comando** que acompanha o Prometheus
(instalado no mesmo pacote que o binário `prometheus`). Ele **não** coleta
métricas e **não** substitui o servidor: serve para validar, depurar e
inspecionar artefatos antes (ou ao lado) de subir o processo longo.

Neste tutorial usamos sobretudo:

```bash
promtool check config monitoring/prometheus.yml
promtool check rules monitoring/bentoml.rules.yml
```

- `check config` — analisa o YAML de scrape/regras referenciadas; falha se a
  sintaxe estiver errada, se um `rule_files` apontar para caminho inexistente
  ou se a versão do Prometheus rejeitar algum campo.
- `check rules` — valida o arquivo de recording rules e alertas (expressões
  PromQL, `for`, labels).

Os dois comandos devem terminar com `SUCCESS`. Outros subcomandos existem
(`query`, `tsdb`, …); para a aula, a validação antes do `prometheus …` já
evita meia hora a caçar um traço de indentação.

Valide os arquivos antes de subir qualquer processo:

```bash
promtool check config monitoring/prometheus.yml
promtool check rules monitoring/bentoml.rules.yml
```

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
Se aparecer `DOWN`, confirme que o BentoML continua rodando (`just serve` — ele
**não** sobe sozinho), que sua porta é 3000 e que
`curl http://127.0.0.1:3000/metrics` responde.

**Prometheus errado na porta 9090.** O arquivo
[`monitoring/prometheus.yml`](../monitoring/prometheus.yml) deste repositório
define **apenas** o job `bentoml-imagens` → `127.0.0.1:3000`. Se
`/targets` listar cadvisor, flower, exporters de outros sistemas etc., você
está olhando **outra** instância de Prometheus (já residente na máquina), não
a da aula. Nesse caso:

1. Confirme se o processo que você iniciou usou
   `--config.file=monitoring/prometheus.yml` deste repo.
2. Se a porta 9090 já estiver ocupada, pare essa instância **ou** suba a da
   aula noutra porta (ex. `9091`) e use essa URL no restante do tutorial:
   `--web.listen-address=127.0.0.1:9091`.
3. A demo sintética da [aula 010](../010_prometheus_promql/README.md) usa
   **9100** de propósito, para não brigar com um Prometheus “de produção”
   local na 9090.

## 4. Gere tráfego e consulte a latência

Você já tem o balcão (`/metrics`) e o livro-razão (Prometheus). Falta movimento
na porta: sem requisições HTTP, os contadores de inferência ficam em zero e a
taxa média some no gráfico. O próximo passo é mandar imagens de verdade pelo
mesmo caminho que um cliente usaria.

Escolha um arquivo que exista em `samples/` (por exemplo sob `samples/demo` ou
`samples/beaches`). Se você já rodou a análise que cria agrupamentos, também
pode pegar algo em `samples/clustered/`. O que importa é um `.jpg` ou `.webp`
legível pelo serviço.

O trecho abaixo pede ao shell o primeiro arquivo que encontrar e, em seguida,
repete dez vezes a receita `just curl-inference-resize`: cada volta é um
`POST` multipart para `/inference-resize`, com largura e altura 256, gravando
a resposta em `/tmp/resized.png` (o arquivo de saída é sobrescrito; o que
conta para a métrica é a **chamada**, não a diversidade do PNG).

```bash
IMAGE=$(find samples/demo samples/beaches -type f \( -name '*.jpg' -o -name '*.webp' \) | head -1)

for i in $(seq 1 10); do
  just curl-inference-resize "$IMAGE" /tmp/resized.png 256 256
done
```

Por baixo do `just`, o repositório monta um `curl` autenticado ao contrato do
BentoML (campos de formulário `image`, `width`, `height`, URL
`http://127.0.0.1:3000/inference-resize`). O loop `seq 1 10` não é paralelo:
dez idas e voltas em série. O intervalo entre iterações inclui o tempo de
processamento da imagem; por isso a taxa observada no Prometheus raramente
será “exatamente 10 por minuto” — e não precisa ser. O objetivo é **gerar
amostras** nos contadores `bentoml_service_request_total` e nos buckets de
`bentoml_service_request_duration_seconds`.

Se `IMAGE` sair vazio, o `find` não achou arquivos: confira se `samples/demo`
existe no clone. Se o `curl` falhar com conexão recusada, o `just serve` do
terminal 1 não está no ar. Se receber HTTP 4xx/5xx, a métrica ainda pode
registrar o código em labels (`http_response_code`); mesmo assim, prefira
chamadas `200` para a primeira leitura de latência.

Espere pelo menos cinco segundos — um ciclo completo do `scrape_interval` —
para a nova coleta entrar no TSDB. Na interface
<http://127.0.0.1:9090/query>, comece pela taxa de requisições por endpoint.

### Taxa por endpoint

```promql
sum by (endpoint) (rate(bentoml_service_request_total[1m]))
```

Leitura de dentro para fora:

1. `bentoml_service_request_total` — contador cumulativo de requisições (por
   combinação de labels: `endpoint`, código HTTP, etc.).
2. `[1m]` — janela de um minuto de amostras desse contador.
3. `rate(...[1m])` — estima o crescimento **por segundo** ao longo da janela,
   tratando reinícios de processo. A unidade fica em requisições/s.
4. `sum by (endpoint) (...)` — soma as séries que compartilham o mesmo
   `endpoint` (por exemplo agregando códigos 200 e 500 da mesma rota),
   preservando uma linha por caminho HTTP.

No **Graph**, você deve ver picos ou patamares coincidentes com o loop. No
**Table**, um valor por `endpoint` no instante avaliado.

### Percentil 95 (p95) do tempo de resposta

O **percentil 95**, ou **quantil 0,95**, responde: “abaixo de que duração
estão cerca de 95% das observações?” A média pode parecer saudável enquanto a
cauda lenta (poucas requisições muito demoradas) estraga a experiência. Em
APIs de inferência, o p95 por `endpoint` mostra se `/inference-resize` puxa a
latência; em checkout de e-commerce, um p95 alto com média baixa costuma
indicar uma minoria de carrinhos problemáticos.

Exemplo numérico com dez latências já ordenadas (ms):
`20, 22, 24, 25, 28, 30, 35, 40, 80, 200`. A mediana (p50) fica perto de 29 ms;
o p95 cai na cauda entre 80 e 200 ms; a média (~50 ms) esconde essa cauda. Com
histogramas Prometheus não temos a lista completa: estimamos o quantil a
partir dos buckets `le`.

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

Passo a passo:

1. Seleciona as séries `…_duration_seconds_bucket` cujos `endpoint` casam com
   a expressão regular (rotas de inferência deste serviço).
2. `rate(...[1m])` transforma contadores cumulativos de bucket em taxas na
   janela recente (latência **agora**, não desde o boot).
3. `sum by (le, endpoint)` preserva o limite `le` (obrigatório para
   reconstruir o histograma) e o `endpoint`.
4. `histogram_quantile(0.95, …)` interpola o quantil 0,95 sobre esses buckets.

O resultado está em **segundos**. Multiplique por 1000 se quiser ler em ms.
`histogram_quantile` **estima** o p95; não devolve a 95ª requisição literal.
Se a janela tiver poucas observações, o valor oscila ou vira `NaN`.

## 5. Detecte uma anomalia de tempo de resposta

Até aqui você leu o passado imediato com consultas manuais. As **regras** em
[`monitoring/bentoml.rules.yml`](../monitoring/bentoml.rules.yml) automatizam
duas ideias: (1) **gravar** de tempos em tempos o p95 de um minuto como uma
série nova, estável, fácil de colocar em gráfico; (2) **comparar** esse p95
com o que tem sido “normal” na última meia hora, e só então falar em alerta.

### Recording rule: um atalho nomeado para o p95

```yaml
- record: bentoml:http_request_duration_seconds:p95_1m
  expr: |
    histogram_quantile(
      0.95,
      sum by (le, endpoint) (
        rate(bentoml_service_request_duration_seconds_bucket{
          endpoint=~"/(blur|grayscale|resize)"
        }[1m])
      )
    )
```

A cada `evaluation_interval` (5 s neste repo), o Prometheus avalia a expressão
e **escreve o resultado** na série
`bentoml:http_request_duration_seconds:p95_1m` (ainda particionada por
`endpoint`). Consultar esse nome é mais barato e mais legível do que repetir o
bloco `histogram_quantile` em todo painel.

```promql
bentoml:http_request_duration_seconds:p95_1m
```

Interpretação: “p95 estimado das durações, em segundos, na janela de um minuto
que a regra usa”, por rota. Não é o p95 de todas as requisições dos últimos
30 minutos — esse seria outro `histogram_quantile` com `[30m]`.

### Alerta: três desvios acima da média móvel, por um minuto

```yaml
- alert: BentoMLResponseTimeAnomaly
  expr: |
    bentoml:http_request_duration_seconds:p95_1m
      >
    avg_over_time(bentoml:http_request_duration_seconds:p95_1m[30m])
      + 3 * stddev_over_time(bentoml:http_request_duration_seconds:p95_1m[30m])
  for: 1m
```

Em prosa:

1. Tome o p95 atual (a série gravada acima).
2. Calcule a **média** dos valores dessa série nos últimos 30 minutos
   (`avg_over_time`).
3. Calcule o **desvio padrão** na mesma janela (`stddev_over_time`).
4. Some média + 3× desvio: um teto adaptativo. Se o p95 atual ultrapassa esse
   teto, a condição do alerta é verdadeira.
5. `for: 1m` exige que a condição permaneça verdadeira nas avaliações durante
   um minuto antes de passar de `pending` a `firing`.

Estados na UI <http://127.0.0.1:9090/alerts> ou na consulta:

```promql
ALERTS{alertname="BentoMLResponseTimeAnomaly"}
```

- **`pending`** — a expressão já é verdadeira, mas ainda não durou `for: 1m`.
- **`firing`** — durou o suficiente. Isso **não** envia e-mail sozinho:
  notificação exige Alertmanager (ou outro receptor), fora deste tutorial.

### Por que a linha de base começa frágil

Nos primeiros minutos há poucos pontos da série `…:p95_1m`. Com uma ou duas
amostras, o desvio padrão pode ser **zero**: aí média + 3×0 = média, e
qualquer flutuação mínima “dispara” a desigualdade — ou o contrário, nada
dispara de forma estável. Deixe carga **normal** acumular dezenas de minutos
antes de levar o alerta a sério.

Três desvios-padrão são um **ponto de partida didático**, não um limite
universal. Tráfego com horário de pico, lotes noturnos ou duas populações
misturadas (imagem pequena vs grande) produzem distribuições sazonais ou
multimodais: a média±kσ sobre o p95 de um minuto pode ser cega demais ou
alarmista demais. Depois de observar o padrão real, ajuste:

- a janela do p95 (`[1m]` na recording rule),
- a janela da linha de base (`[30m]`),
- o multiplicador (`3`),
- o `for`.

Uma regra adaptativa inclui o presente na média: enquanto a latência sobe de
forma lenta e monótona, a linha de base sobe junto e pode “engolir” a anomalia.
Picos curtos são o que este desenho pega melhor.

## 6. Encerre e limpe

Pressione `Ctrl+C` nos terminais do Prometheus e do BentoML. Os dados desta aula
ficam em `/tmp/bentoml-imagens-prometheus`; você pode apagá-los quando não
precisar mais do histórico.

## Continuação (aula 010)

Com a coleta em `3000`/`9090` funcionando, a
[aula 010](../010_prometheus_promql/README.md) trabalha `/metrics` e PromQL na
UI do Prometheus (`9090`). O painel Streamlit (histograma/CDF) é a
[aula 015](../015_prometheus_histcdf_streamlit/README.md) em `127.0.0.1:8516` —
não substitui o BentoML em `3000` nem a UI do Prometheus.

## Referências

- [Métricas e integração Prometheus do BentoML](https://docs.bentoml.org/en/latest/build-with-bentoml/observability/metrics.html)
- [Primeiros passos com Prometheus](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [Instalação do Prometheus](https://prometheus.io/docs/prometheus/latest/installation/)
- [Configuração do Prometheus](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [Recording rules e alertas](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
