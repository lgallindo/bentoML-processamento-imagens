# Proposal

## Why

The root project teaches BentoML HTTP transport with three Pillow filters and only three sample images. For a follow-on educational lesson we need a self-contained in-repo sibling that introduces a training corpus, reference brightness/color histograms, and packaging one existing operation as a BentoML model—without adding neural network weights or changing the baseline lesson.

## What Changes

- Add a full sibling copy of the project at `01_corpus_histograms_model/` (Option A: independent runnable tree inside this repository).
- Leave the repository root service, samples, and README as lesson 0 (unchanged behavior).
- In the sibling: reproducible download of at least 50 training images under its `samples/`, plus tracked manifest metadata (hashes/seeds/URLs); prefer not bloating git with large binaries when a download recipe suffices.
- In the sibling: offline extraction of brightness and color levels into `reference_stats.json` (or equivalent) treated as the training-data reference.
- In the sibling: new HTTP endpoint that returns aggregate histograms / reference stats for that corpus (e.g. `GET /training-histograms`).
- In the sibling: turn **`/grayscale`** into a BentoML **`picklable_model`**-backed path (same Pillow `convert("L")` semantics). `/blur` and `/resize` remain direct Pillow calls.
- Sibling-local scripts/just recipes for download, stats build, and model save.
- Later educational variants (`02_…`, real ML weights, etc.) are **out of scope** for this change.

## Capabilities

### New Capabilities

- `sample-corpus`: Reproducible training-image corpus (≥50) under the sibling `samples/`, with download/manifest workflow.
- `training-reference-histograms`: Offline reference brightness/color aggregates and an HTTP API to expose training histograms/stats.
- `grayscale-picklable-model`: `/grayscale` served via a saved BentoML picklable model (no new learned weights); other image endpoints stay classical.

### Modified Capabilities

- _(none — no existing specs in this project)_

## Impact

- **New tree:** `01_corpus_histograms_model/` (copy of project files + new scripts, stats artifact, model-save recipe, sibling README in pt_BR formal per project language rules).
- **APIs (sibling only):** new training-histograms endpoint; `/grayscale` loads/calls a model ref; `/blur` and `/resize` unchanged in behavior.
- **Dependencies:** still BentoML + Pillow for inference; download may use stdlib/`urllib` or a small HTTP client already available—no torch/onnx/new ML framework.
- **Git/disk:** sample binaries policy (gitignore + manifest vs commit) decided in design; research mount has limited free space—keep images modest.
- **Does not:** modify root `service.py` behavior; add real ML models; implement deferred `02_+` variants.
