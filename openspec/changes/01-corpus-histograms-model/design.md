# Design

## Context

See `proposal.md` for motivation. Repository root is a ~35-line BentoML `ImageProcessor` (`blur` / `grayscale` / `resize` via Pillow) with three WebP demos. BentoML **1.4.39** exposes `bentoml.models` and `bentoml.picklable_model`. This change adds one in-repo full sibling only; root stays lesson 0.

## Goals / Non-Goals

**Goals:**

- Self-contained runnable tree at `01_corpus_histograms_model/`.
- Reproducible ≥50-image corpus + manifest; offline brightness/color reference stats; HTTP exposure of those stats.
- Package `/grayscale` as a picklable BentoML model with identical classical semantics.
- Keep student-facing sibling README in pt_BR formal (LANG-001); code identifiers in en_US.

**Non-Goals:**

- Changing root `service.py` behavior.
- Real learned weights, runners for blur/resize, or `02_+` variants.
- Committing large binary dumps if a download+manifest path works (prefer restore-from-manifest).

## Decisions

### D1 — Full sibling copy (Option A), path fixed
**Choice:** `01_corpus_histograms_model/` at repo root.  
**Why:** Independent `just serve` / `uv sync` per lesson; no path confusion.  
**Alt:** Overlay patches on one tree — rejected (user locked Option A).

### D2 — Image source: Lorem Picsum with fixed seeds
**Choice:** `https://picsum.photos/seed/bentoml-edu-{i}/640/480` (or similar fixed size), `i = 1..N` with `N >= 50`.  
**Why:** No API key, deterministic seeds, small JPEGs, fine for class demos.  
**Alt:** Wikimedia Commons (better provenance, more brittle); academic datasets (wrong “photo processing” story).

### D3 — Git policy for binaries
**Choice:** Gitignore `01_corpus_histograms_model/samples/train_*` (and similar); track `samples/MANIFEST.json` (seed, URL, sha256, path); keep the three CESAR demo webps if copied into the sibling for curl recipes.  
**Why:** Avoid repo bloat on the research mount; manifest restores corpus.  
**Alt:** Commit all 50 images — only if class must work fully offline without network (revisit if needed).

### D4 — Reference stats artifact
**Choice:** `01_corpus_histograms_model/reference_stats.json` built offline (Pillow): per-image luminance mean; aggregate 256-bin histograms for L and R/G/B (or grayscale+RGB); top-level `n_images`, percentiles for brightness.  
**Why:** Transparent “training reference” without pretending to train.  
**Alt:** Parquet/numpy — heavier deps for little teaching gain.

### D5 — Histograms API shape
**Choice:** `GET /training-histograms` returning JSON from the precomputed file (load at service init or on demand with clear error if missing). No image upload on this route.  
**Why:** Matches “reference corpus” teaching point; simple to curl/Swagger.  
**Alt:** `POST` with optional compare-to-upload — deferred to a later variant.

### D6 — Grayscale via `bentoml.picklable_model`
**Choice:** Save a small picklable callable/class that applies `Image.convert("L")`; sibling service loads `image-grayscale:latest` (name TBD in tasks) and invokes it from `@bentoml.api def grayscale`. Document `just save-grayscale-model` (or equivalent) before first serve.  
**Why:** Real model store / versioning lesson without torch.  
**Alt:** Custom `bentoml.models.create` file bundle — more ceremony; picklable is the direct fit for a Python function.

### D7 — Bootstrap the sibling
**Choice:** Copy root project files (`service.py`, `pyproject.toml`, `uv.lock`, `justfile`, `bentofile.yaml`, `samples/` demos, minimal docs) into the sibling, then layer scripts and service edits. Prefer sharing the same lockfile content initially (copy) so versions match lesson 0.  
**Why:** True independent variant; TECH-010 still applies inside sibling (use `uv`, don’t hand-edit lock).  
**Alt:** Symlink deps — breaks “full copy” pedagogy.

### D8 — Validation / errors
**Choice:** Reuse root `ImageInput` / `WrapValidator` pattern for image POSTs; histograms endpoint returns structured error if `reference_stats.json` absent.  
**Why:** Preserve the 400-vs-500 lesson already taught at root.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Picsum rate limits / offline classroom | Manifest + optional committed tiny subset; document failure mode |
| Students forget `save-grayscale-model` | README + just recipe; clear startup error if model missing |
| Drift between root and sibling copies | Accept for pedagogy; later variants may document sync rules |
| Disk pressure on research mount | Modest JPEG size; gitignore binaries; no `--force` cleanup of `.lake` |
| “Fake ML” confusion | README states explicitly: classical Pillow packaged as a model, not trained weights |

## Migration Plan

1. Add sibling tree and scripts (no change to root runtime).
2. Run download → build stats → save model → `just serve` from sibling cwd.
3. Rollback: delete sibling folder / ignore it; root unaffected.

## Open Questions

- Exact BentoML model tag string (`image-grayscale` vs `grayscale-pillow`) — pick during apply; does not change specs.
- Whether sibling keeps monitoring/ docs copies or strips them for brevity — default: copy then trim only if noisy; does not change specs.
