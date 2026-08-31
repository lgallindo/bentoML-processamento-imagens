default:
    @just --list

# Start the BentoML development server with automatic reload.
serve port="3000":
    python -m bentoml serve service:ImageProcessor --reload --port {{port}}

# Open the Swagger UI when xdg-open is available; otherwise print its URL.
swagger port="3000":
    @url="http://localhost:{{port}}/docs"; \
    if command -v xdg-open >/dev/null 2>&1; then \
        xdg-open "$url" >/dev/null 2>&1 || printf 'Swagger UI: %s\n' "$url"; \
    else \
        printf 'Swagger UI: %s\n' "$url"; \
    fi

# Submit an image to the grayscale API and save the returned image.
curl-grayscale image output="grayscale.png" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        "http://localhost:{{port}}/grayscale" \
        --output "{{output}}"

# Submit an image to the blur API and save the returned image.
curl-blur image output="blur.png" radius="4.0" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        --form "radius={{radius}}" \
        "http://localhost:{{port}}/blur" \
        --output "{{output}}"

# Submit an image to the resize API and save the returned image.
curl-resize image output="resized.png" width="256" height="256" port="3000":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        --form "width={{width}}" \
        --form "height={{height}}" \
        "http://localhost:{{port}}/resize" \
        --output "{{output}}"
