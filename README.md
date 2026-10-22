# Processamento de imagens com BentoML

Um serviço web que recebe uma imagem por HTTP, aplica um filtro e devolve a
imagem pronta. São três operações: tons de cinza, desfoque e redimensionamento.

O código todo tem **35 linhas** e está em [`service.py`](service.py). Nele não
existe nenhuma rota, nenhuma porta, nenhum leitor de formulário e nenhum
cabeçalho HTTP escrito à mão. Existem *anotações de tipo* — e o BentoML lê essas
anotações e constrói a API a partir delas. É isso que este projeto tem para
ensinar, e você vai conferir com os próprios olhos na terceira seção.

---

## As duas ferramentas do terminal

**`uv`** cuida do Python e das bibliotecas. Ele lê o `pyproject.toml` (quais
bibliotecas o projeto precisa) e o `uv.lock` (a versão exata de cada uma) e monta
a pasta `.venv/`. Como o `uv.lock` fixa as versões, a turma inteira termina com o
mesmo ambiente. Ele também baixa o Python 3.13 que este projeto pede, sem mexer
no Python que já existe na sua máquina. E você **não precisa ativar ambiente
nenhum**: o comando `uv run` entra no `.venv/` sozinho, a cada chamada. É daí que
vem o `--no-active` espalhado pelo justfile — ele manda o `uv` ignorar qualquer
ambiente que você tenha ativado na mão e usar sempre o deste projeto.

**`just`** guarda comandos longos debaixo de nomes curtos. Em vez de digitar
`uv run --no-active bentoml serve service:ImageProcessor --reload --port 3000`,
você digita `just serve`. Esses apelidos são chamados de **receitas** e ficam num
arquivo de texto comum, o [`justfile`](justfile), que você pode abrir e ler. O
`just` não faz parte do Python nem do BentoML: existe só para você não decorar
comando nenhum. Rode `just` sozinho para ver a lista.

---

## Instalação

As duas ferramentas se instalam uma vez por máquina, não uma vez por projeto. Se
você já tiver alguma, pule.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # uv
uv tool install rust-just                         # just
```

Não é engano: o pacote se chama `rust-just`, mas o comando que ele instala se
chama `just`. Feche e reabra o terminal, e confira:

```bash
uv --version && just --version
```

O `just` precisa ser 1.31 ou mais novo — evite instalar por `apt`, que em várias
distribuições traz uma versão velha demais. Agora, **dentro da pasta do
projeto**, monte o ambiente:

```bash
just sync
```

Isso cria a pasta `.venv/`, com cerca de 143 MB. Este projeto **não baixa modelo
de machine learning**, então não existe aqui aquela primeira execução de vários
minutos: depois do `sync`, o servidor sobe em poucos segundos.

---

## 1. Rodando: por que dois terminais

Um servidor é um programa que **sobe e fica esperando**. Ele não termina, não
devolve o cursor e não faz nada por conta própria — fica parado até alguém pedir
algo. Quem pede é o **cliente**. Você vai ser os dois, então precisa de duas
janelas de terminal.

**Terminal 1 — o servidor.** Deixe esta janela aberta:

```bash
just serve
```

Espere a linha `Service ImageProcessor initialized`, que aparece em 2 a 4
segundos. Este terminal agora parece travado. **Ele não está travado**: está
ocupado sendo um servidor. É assim que tem que ser.

**Terminal 2 — o cliente.** Aqui você faz os pedidos:

```bash
just curl-inference-grayscale samples/demo/cesar-fachada-1.webp
```

Isso manda `samples/demo/cesar-fachada-1.webp` para o servidor e salva a resposta em
`grayscale.png`, na pasta do projeto. Abra o arquivo: é a mesma foto em tons de
cinza. As três imagens de exemplo estão em [`samples/demo/`](samples/demo/).

Para derrubar o servidor, `Ctrl+C` no terminal 1.

> **Experimento.** Feche o terminal 1 (ou dê `Ctrl+C`) e rode a receita do
> terminal 2 de novo. Antes de rodar, escreva o que você espera ver. A mensagem é
> esta:
>
> ```
> curl: (7) Failed to connect to localhost port 3000 after 0 ms: Could not connect to server
> ```
>
> É o cliente dizendo que não há ninguém do outro lado. Guarde esse texto: é o
> erro que você mais vai encontrar na vida com servidores, e ele nunca quer dizer
> que o seu código está errado.

---

## 2. Agora olhe o `service.py`

Com o servidor de pé, abra <http://localhost:3000/> no navegador (ou rode
`just swagger`). Você vai encontrar uma página de documentação interativa, a
**Swagger UI**, com os três endpoints listados, um campo de upload de arquivo em
cada um e um botão para testar sem sair do navegador.

Agora abra [`service.py`](service.py) e procure o código que gera essa página.
Não existe. Procure o código que lê o arquivo enviado no formulário. Também não
existe. O arquivo inteiro tem 35 linhas, das quais uns 15 fazem algum trabalho:

```python
@bentoml.api
def resize(self, image: ImageInput, width: Positive = 256, height: Positive = 256) -> PILImage:
    return image.resize((width, height))
```

Essas três linhas produzem, sozinhas:

| o que está escrito no Python | o que o BentoML construiu com isso |
|---|---|
| `@bentoml.api` | uma rota `POST /inference-resize` |
| `image: ImageInput` | um campo de upload de arquivo, decodificado como imagem |
| `width: Positive = 256` | um campo inteiro opcional, padrão 256, **recusado se for ≤ 0** |
| `-> PILImage` | uma resposta PNG, com o `Content-Type` correto |

A anotação de tipo deixou de ser um comentário para o leitor humano e passou a
ser a especificação da API. Você descreve **o que** entra e sai; o BentoML
resolve o **como**. De graça vieram também `/healthz`, `/livez`, `/readyz` e
`/metrics`, que você igualmente não escreveu.

> **Experimento.** Com o servidor de pé no terminal 1, mude em `service.py` o
> `width: Positive = 256` para `width: Positive = 64` e salve. **Antes de fazer
> qualquer requisição**, olhe o terminal 1. Aparecem duas linhas novas:
> `Service instance cleanup finalized` e `Service ImageProcessor initialized` — o
> servidor se reiniciou sozinho, porque `just serve` passa a opção `--reload`.
> Agora recarregue a Swagger UI e veja o padrão do campo. Depois rode
> `just curl-inference-resize samples/demo/cesar-fachada-1.webp saida.png` e confira o tamanho
> da imagem gerada. Por fim, desfaça a mudança.

---

## 3. Quando você manda coisa errada: 400 ou 500?

Todo código de resposta HTTP que começa com **4 diz "você errou"** (o cliente
mandou algo inválido) e todo código que começa com **5 diz "eu errei"** (o
servidor quebrou). Essa diferença não é decoração: ela informa quem tem que
consertar o quê. Um serviço que responde 500 para um arquivo inválido está
mentindo — e mandando a pessoa errada caçar o problema.

Mande um arquivo que não é imagem:

```bash
echo "nao sou uma imagem" > lixo.txt
curl -X POST -F "image=@lixo.txt" http://localhost:3000/inference-grayscale
```

A resposta:

```json
{"error":"1 validation error for Input","detail":[{"type":"value_error",
"loc":["image"],"msg":"Value error, o arquivo enviado não é uma imagem válida"}]}
```

Status **400**, e a mensagem diz exatamente qual campo está errado e por quê.

Aqui o `curl` está escrito à mão de propósito, para você ver uma vez o que as
receitas escondem: este comando é tudo o que `just curl-inference-grayscale` faz por baixo.
O `just` é só um apelido.

Há um motivo prático também. As receitas `curl-inference-grayscale`, `curl-inference-blur` e
`curl-inference-resize` usam a opção `--fail`, que descarta o corpo da resposta quando o
status é de erro — com elas você veria apenas `curl: (22) The requested URL
returned error: 400`, sem a explicação. Quando quiser ler o erro sem escrever o
`curl` inteiro, existe uma receita só para isso:

```bash
just curl-erro grayscale lixo.txt
```

Esse 400 não veio de graça. O Pillow, ao tentar abrir um `.txt` como imagem,
levanta um `OSError`, que o pydantic não reconhece como problema de validação —
o resultado natural seria **500**. As linhas 9 a 15 de `service.py` existem só
para reempacotar esse erro como `ValueError`, que o pydantic entende e traduz
para 400. Foram sete linhas de código para não mentir sobre de quem é a culpa.

> **Experimento.** Peça um redimensionamento com largura zero:
> `curl -X POST -F "image=@samples/demo/cesar-fachada-1.webp" -F "width=0" -F "height=100" http://localhost:3000/inference-resize`
> Antes de rodar, responda: erro seu ou erro do servidor? Qual código você espera?
> Depois tente também `-F "radius=abc"` no `/inference-blur`, um `GET` em `/inference-grayscale` e um
> `POST` em `/nope`. São quatro erros diferentes e três códigos diferentes
> (400, 405 e 404). Explique cada um.

---

## A lição

> O BentoML não te poupou de escrever um filtro de imagem — o Pillow já fazia
> isso. Ele te poupou de escrever a **camada de transporte**: rota, parsing,
> validação, serialização e documentação. Você declarou os tipos e ganhou uma API
> que já sabe recusar entrada inválida com o código certo.

---

## Referência da API

Todos os endpoints são `POST`, recebem a imagem num formulário no campo `image` e
devolvem **PNG**, qualquer que seja o formato de entrada.

| endpoint | o que faz | parâmetros além da imagem |
|---|---|---|
| `/inference-grayscale` | converte para tons de cinza | — |
| `/inference-blur` | desfoque gaussiano | `radius` (decimal, padrão `1.0`) |
| `/inference-resize` | redimensiona | `width`, `height` (inteiros > 0, padrão `256`) |

## Receitas disponíveis

```bash
just                    # lista todas as receitas
just sync               # monta ou atualiza a .venv/
just serve              # sobe o servidor na porta 3000
just swagger            # abre a documentação interativa no navegador

just curl-inference-grayscale samples/demo/cesar-fachada-1.webp
just curl-inference-blur         samples/demo/cesar-fachada-1.webp desfoque.png 8.0
just curl-inference-resize       samples/demo/cesar-fachada-1.webp reduzida.png 320 200

just curl-erro grayscale lixo.txt                    # mostra o erro, não salva imagem
just curl-erro resize foto.webp 3000 width=0         # campos extras vão soltos no fim

just build              # empacota o serviço num bento, seguindo o bentofile.yaml
just list               # lista os bentos já empacotados nesta máquina
```

Os argumentos das receitas `curl-*` são **posicionais**: para mudar só a porta,
você precisa passar todos os anteriores — `just curl-inference-resize foto.webp saida.png
320 200 3001`. Para subir o servidor em outra porta: `just serve 3001`.

Os arquivos gerados (`grayscale.png`, `blur.png`, `resized.png`) estão no
`.gitignore`.

## Quando algo dá errado

| Mensagem | O que fazer |
|---|---|
| `curl: (7) Failed to connect to localhost port 3000` | o servidor não está de pé. Volte ao terminal 1 e rode `just serve` |
| um rastro de erro enorme terminando em `OSError: [Errno 98] Address already in use` | algo já ocupa a porta. Ignore o rastro e leia só a **última** linha; suba em outra porta com `just serve 3001` |
| o terminal do `serve` parece travado | é assim mesmo: ele está ocupado sendo servidor. Use a outra janela |
| `curl: (22) ... returned error: 400` | você mandou algo inválido. Repita com `curl` na mão, sem `--fail`, para ler a explicação |
| `command not found: just` | feche e reabra o terminal depois de `uv tool install rust-just` |

## Onde olhar no código

| Arquivo | O que tem dentro |
|---|---|
| [`service.py`](service.py) | o serviço inteiro: 3 endpoints em 35 linhas |
| [`justfile`](justfile) | as receitas, e o comando de verdade que cada uma esconde |
| [`pyproject.toml`](pyproject.toml) | as bibliotecas que o projeto usa |
| [`bentofile.yaml`](bentofile.yaml) | o que entra no pacote; é o que `just build` lê para gerar um *bento* |
| [`samples/demo/`](samples/demo/) | as três imagens de exemplo (CESAR) |
| [`samples/beaches/`](samples/beaches/) | corpus temático (praias) |
| [`samples/forests/`](samples/forests/) | lote de produção / shift (florestas) |
| [`samples/balls/`](samples/balls/) | contaminantes (nem praia nem floresta) |

Vale ler os comentários do `service.py`: eles explicam não só o que o código
faz, mas por que algumas decisões foram tomadas.

[`001_histogram_cdf_cli`](001_histogram_cdf_cli/README.md)
