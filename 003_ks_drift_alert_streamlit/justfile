default:
    @just --list

sync:
    uv sync --no-active

download-samples:
    @echo "Corpus temático: $(git rev-parse --show-toplevel)/samples/beaches/"
    @echo "Drift: samples/forests/  |  Contingência: samples/balls/"
    @echo "Confirme: just -f $(git rev-parse --show-toplevel)/justfile verify-themed-samples"

extract-features:
    uv run --no-active python scripts/extract_image_features.py

build-corpus-stats:
    uv run --no-active python scripts/build_corpus_stats.py

# Offline: control (beaches offset 50 = disjunto do treino[:50]) + forests
build-demo-batches:
    uv run --no-active python scripts/build_batch_from_theme.py beaches --name control --offset=50 --count=50
    uv run --no-active python scripts/build_batch_from_theme.py forests --name forests --offset=0 --count=50

# Contingência visual (bolas). Lote misto praias+florestas → aula 007.
build-contingency-batches:
    uv run --no-active python scripts/build_batch_from_theme.py balls --name balls --offset=0 --count=50

save-grayscale-model:
    uv run --no-active python scripts/save_grayscale_model.py

serve port="3333":
    uv run --no-active bentoml serve service:ImageProcessor --reload --port {{port}}

streamlit port="8503":
    uv run --no-active streamlit run app.py --server.port {{port}} --server.headless true

clear-request-features:
    uv run --no-active python -c "from pathlib import Path; p=Path('request_features'); p.mkdir(exist_ok=True); [f.unlink() for f in p.glob('*.json')]; print('limpo request_features/')"

exercise-theme theme="forests" port="3333" offset="0" count="12":
    uv run --no-active python scripts/exercise_theme.py {{theme}} --port={{port}} --offset={{offset}} --count={{count}}

snapshot-batch name:
    uv run --no-active python scripts/snapshot_batch.py {{name}} --clear-source

# Contingência bolas:
#   just build-contingency-batches && just verify-ks-alert balls

curl-inference-grayscale image output="grayscale.png" port="3333":
    curl --fail --show-error --request POST \
        --form "image=@{{image}}" \
        "http://localhost:{{port}}/inference-grayscale" \
        --output "{{output}}"

# Verifica D/p/alerta nos lotes em batch_stats/ (sem UI)
verify-ks-alert batch="forests":
    uv run --no-active python scripts/verify_ks_alert.py {{batch}}

generate-illustrations:
    uv run --no-active python scripts/generate_illustrations.py

test:
    uv run --no-active pytest -q
