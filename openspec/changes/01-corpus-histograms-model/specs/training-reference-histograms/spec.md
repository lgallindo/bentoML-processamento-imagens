# Spec Delta

## Purpose

Exposes brightness and color distributions of the sibling training corpus as durable reference statistics and via an HTTP API, teaching corpus-level measurement without claiming gradient-based training.

## ADDED Requirements

### Requirement: Offline reference stats from the training corpus
The sibling SHALL provide a documented offline workflow that reads the training images under its `samples/` corpus and writes a durable reference-stats artifact containing aggregate brightness and color-level information for that corpus.

#### Scenario: Stats artifact created from corpus
- **WHEN** the offline reference-stats workflow runs against a corpus of at least fifty training images
- **THEN** a reference-stats file is written that includes luminance (or brightness) aggregates and per-channel color histogram or level summaries derived from those images

### Requirement: Training histograms HTTP endpoint
The sibling service SHALL expose an HTTP endpoint that returns the training corpus reference histograms/stats (JSON). The endpoint MUST NOT require an uploaded image.

#### Scenario: Client fetches training histograms
- **WHEN** a client requests the training-histograms endpoint on a running sibling service that has a built reference-stats artifact
- **THEN** the response status is success and the JSON body includes the number of images summarized and brightness/color histogram or level data

#### Scenario: Missing reference stats
- **WHEN** a client requests the training-histograms endpoint and the reference-stats artifact is missing or unreadable
- **THEN** the service responds with a client- or server-appropriate error status and does not invent empty successful histograms

### Requirement: Reference stats describe the corpus, not a single request
The training-histograms endpoint MUST return aggregate reference data for the stored training corpus, not a histogram computed solely from a single ad-hoc upload in that request.

#### Scenario: Endpoint ignores upload-only workflow
- **WHEN** a client calls the training-histograms endpoint without uploading an image
- **THEN** the response reflects the precomputed corpus reference stats
