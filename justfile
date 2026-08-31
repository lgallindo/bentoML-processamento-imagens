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
curl-grayscale image output="grayscale.png" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        "http://localhost:{{port}}/grayscale" \
        --output "{{output}}"

# Envia uma imagem para a API blur e salva a imagem retornada.
curl-blur image output="blur.png" radius="4.0" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        --form "radius={{radius}}" \
        "http://localhost:{{port}}/blur" \
        --output "{{output}}"

# Envia uma imagem para a API resize e salva a imagem retornada.
curl-resize image output="resized.png" width="256" height="256" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        --form "width={{width}}" \
        --form "height={{height}}" \
        "http://localhost:{{port}}/resize" \
        --output "{{output}}"
