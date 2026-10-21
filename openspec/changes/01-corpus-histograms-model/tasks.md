# Tasks

## 1. Sibling scaffold

- [x] 1.1 Create `01_corpus_histograms_model/` as a full copy of the runnable root project files (`service.py`, `pyproject.toml`, `uv.lock`, `justfile`, `bentofile.yaml`, `.python-version`, demo `samples/*.webp`, and any needed monitoring/docs trim) and verify `cd 01_corpus_histograms_model && just sync` succeeds
- [x] 1.2 Extend sibling `.gitignore` for `samples/train_*` (and related download outputs) while keeping demo webps trackable; verify `git check-ignore` matches train artifacts only
- [x] 1.3 Add sibling README chapter in pt_BR formal describing corpus, histograms, and grayscale-as-model (explicitly: no neural weights) and verify the documented directory layout matches the tree

## 2. Sample corpus

- [x] 2.1 Implement `scripts/download_samples.py` (Picsum fixed seeds, N≥50, writes images + `samples/MANIFEST.json` with id/seed/url/sha256) and verify a dry run creates ≥50 files and a valid manifest
- [x] 2.2 Add `just download-samples` (uv-run, non-interactive) and verify `just download-samples` populates the corpus from a clean train_* state
- [x] 2.3 Add a unit test that validates manifest schema/count invariants (or checksum round-trip on a fixture image) and verify the test passes under `uv run`

## 3. Reference histograms

- [x] 3.1 Implement `scripts/build_reference_stats.py` reading the training corpus into `reference_stats.json` (n_images, brightness aggregates, L/RGB histograms) and verify the file is produced for the downloaded corpus
- [x] 3.2 Add `just build-reference-stats` and verify it fails clearly if fewer than the required training images are present
- [x] 3.3 Add unit tests for histogram/brightness helpers on synthetic PIL images and verify they pass
- [x] 3.4 Add sibling `@bentoml.api` (or equivalent) `GET`-style `/training-histograms` returning JSON from `reference_stats.json`, with a clear error if the artifact is missing; verify with a Tavern (or project-equivalent HTTP) test against a running or test client
- [x] 3.5 Add `just curl-training-histograms` and verify it prints JSON including `n_images` ≥ 50 after stats are built

## 4. Grayscale picklable model

- [x] 4.1 Implement `scripts/save_grayscale_model.py` using `bentoml.picklable_model` to save a Pillow `convert("L")` wrapper under an agreed tag (e.g. `image-grayscale`) and verify `bentoml models list` shows the new model
- [x] 4.2 Add `just save-grayscale-model` and document it as a prerequisite to serve; verify the recipe is non-interactive
- [x] 4.3 Wire sibling `grayscale` API to load/call the saved model; keep `/blur` and `/resize` as direct Pillow; verify grayscale output matches `Image.convert("L")` on a fixture (unit or API test) and blur still works without that model
- [x] 4.4 Add Tavern (or equivalent) coverage for sibling `/grayscale` happy path and verify it passes after model save

## 5. Integration check

- [x] 5.1 From `01_corpus_histograms_model/`, run download → build-stats → save-model → serve smoke (`/training-histograms`, `/grayscale`, `/blur`, `/resize`) and verify all four succeed without modifying root `service.py`
- [x] 5.2 Confirm repository root `samples/` still has exactly the original three demo images and root serve path is untouched (`git diff` on root `service.py` empty for this change’s apply)
