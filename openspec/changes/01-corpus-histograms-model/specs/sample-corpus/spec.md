# Spec Delta

## Purpose

Provides a reproducible training-image corpus of at least fifty images inside the educational sibling so students can treat data as part of the system, not only three demo files.

## ADDED Requirements

### Requirement: Sibling hosts a training corpus of at least fifty images
The educational sibling at `01_corpus_histograms_model/` SHALL provide a `samples/` directory that contains at least fifty training images usable by offline stats tooling and by the sibling service recipes, in addition to any baseline demo images copied from the repository root.

#### Scenario: Corpus meets minimum size after download
- **WHEN** the sibling sample-download workflow completes successfully
- **THEN** `01_corpus_histograms_model/samples/` contains at least fifty training image files

### Requirement: Corpus download is reproducible
The sibling SHALL expose a documented, non-interactive download workflow that fetches training images from a fixed, deterministic source (stable seeds or equivalent) so repeated runs produce the same logical set of images.

#### Scenario: Student reruns download
- **WHEN** a student runs the documented download recipe twice on a clean `samples/` training set
- **THEN** the second run obtains the same seed/URL set recorded in the corpus manifest

### Requirement: Corpus manifest is tracked
The sibling SHALL maintain a tracked manifest (for example JSON) that records identity metadata for each training image (at least a stable id/seed or source URL and a content checksum). Large image binaries MAY be gitignored provided the manifest and download workflow allow full restoration.

#### Scenario: Manifest lists every training image
- **WHEN** the download workflow finishes
- **THEN** the tracked manifest lists an entry for each training image with id/seed or URL and a checksum

### Requirement: Repository root lesson remains intact
Creating or updating the sibling MUST NOT remove or replace the repository root `samples/` three-image demo set used by lesson 0.

#### Scenario: Root samples unchanged by sibling corpus work
- **WHEN** the sibling corpus is populated
- **THEN** the repository root still contains its original three demo images under `samples/`
