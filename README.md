# bentoML-processamento-imagens

Instalar pré-requisitos:

 - uv: [https://github.com/astral-sh/uv?tab=readme-ov-file](https://github.com/astral-sh/uv?tab=readme-ov-file) # Gerenciador de pacotes mais eficiente que o pip, e mais alinhado com boas práticas de engenharia
 - `source .venv/bin/activate` # Ativar o ambiente de servidor. Isso é para Linux, googleie o comando equivalente no PowerShell
 - `uv tool install bentoml` # Instalar o BentoML
 - `uv add pillow` # Instalar Pillow para processamento de imagens
 - `uv sync` # Sincronizar dependências
 - just: [https://just.systems/](https://just.systems/) # Vamos usar isso aqui para criar comandos simples de inicialização e poder digitar just serve ao invés de bentoml serve config1 config2 config3 ...

Iniciar servidor usando:

 - `just serve`

O servidor vai rodar em [http://localhost:3000/](http://localhost:3000/).

## Imagens de exemplo

As imagens de teste ficam em `samples/`, versionadas como arquivos comuns do git
(o projeto nao usa mais git-lfs). Para exercitar as APIs:

 - `just curl-grayscale samples/cesar-fachada-1.webp`
 - `just curl-blur samples/cesar-fachada-1.webp blur.png 8.0`
 - `just curl-resize samples/cesar-fachada-1.webp resized.png 320 200`

Os arquivos gerados (`grayscale.png`, `blur.png`, `resized.png`) ja estao no `.gitignore`.
