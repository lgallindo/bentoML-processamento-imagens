default:
    @just --list

# Instala/atualiza a .venv local a partir do pyproject.toml + uv.lock.
sync:
    uv sync --no-active

# Sobe o servidor de desenvolvimento do BentoML com recarga automática.
serve port="3000":
    uv run --no-active bentoml serve service:ImageProcessor --reload --port {{port}}

# Abre a Swagger UI quando há xdg-open disponível; senão, imprime a URL.
swagger port="3000":
    @url="http://localhost:{{port}}/"; \
    if command -v xdg-open >/dev/null 2>&1; then \
        xdg-open "$url" >/dev/null 2>&1 || printf 'Abra a Swagger UI em: %s\n' "$url"; \
    else \
        printf 'Abra a Swagger UI em: %s\n' "$url"; \
    fi

# Envia uma imagem para a API grayscale e salva a imagem retornada.
curl-inference-grayscale image output="grayscale.png" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        "http://localhost:{{port}}/inference-grayscale" \
        --output "{{output}}"

# Envia uma imagem para a API blur e salva a imagem retornada.
curl-inference-blur image output="blur.png" radius="4.0" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        --form "radius={{radius}}" \
        "http://localhost:{{port}}/inference-blur" \
        --output "{{output}}"

# Envia uma imagem para a API resize e salva a imagem retornada.
curl-inference-resize image output="resized.png" width="256" height="256" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        --form "width={{width}}" \
        --form "height={{height}}" \
        "http://localhost:{{port}}/inference-resize" \
        --output "{{output}}"

# As outras receitas curl-* usam --fail, que descarta a explicação dos erros;
# esta não usa, então mostra o corpo da resposta e o código HTTP.
#
# Campos extras vão soltos no fim, depois da porta:
#     just curl-erro resize foto.webp 3000 width=0 height=100
#
# Use só para investigar erros: numa chamada que dá certo a resposta é uma
# imagem, e os bytes dela vão embaralhar o seu terminal.

# Mostra o corpo e o código HTTP de uma resposta, em vez de salvar a imagem.
curl-erro endpoint image port="3000" *campos:
    @extra=""; for campo in {{campos}}; do extra="$extra --form $campo"; done; \
    curl --silent --show-error --write-out '\nHTTP %{http_code}\n' \
        --request POST --form "image=@{{image}}" $extra \
        "http://localhost:{{port}}/{{endpoint}}"

# Empacota o serviço num bento distribuível, seguindo o bentofile.yaml.
build:
    uv run --no-active bentoml build

# Lista os bentos já empacotados nesta máquina.
list:
    uv run --no-active bentoml list

# Baixa (ou regenera) amostras temáticas a partir de samples/SOURCES.toml.
download-themed-samples:
    uv run --no-active python scripts/download_themed_samples.py download

# Confere sha256 de samples/{beaches,forests,balls}/ contra MANIFEST.json.
verify-themed-samples:
    uv run --no-active python scripts/download_themed_samples.py verify
