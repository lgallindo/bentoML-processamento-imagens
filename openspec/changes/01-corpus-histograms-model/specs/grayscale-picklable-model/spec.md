# Spec Delta

## Purpose

Teaches BentoML model packaging by serving the sibling `/grayscale` operation through a saved picklable model while preserving classical Pillow behavior and leaving blur/resize as direct code paths.

## ADDED Requirements

### Requirement: Grayscale is served via a saved BentoML model
In the educational sibling, the `/grayscale` API SHALL obtain its transformation logic from a BentoML model artifact saved with the picklable-model mechanism (or equivalent BentoML custom/picklable model save), not solely from an inline function defined only inside the request handler.

#### Scenario: Grayscale uses a model reference
- **WHEN** the sibling service handles a valid grayscale request
- **THEN** the conversion is performed by logic loaded from a BentoML model reference previously saved for this lesson

### Requirement: Grayscale output matches classical luminance conversion
For a valid input image, sibling `/grayscale` MUST return an image whose pixels match Pillow's grayscale conversion (`convert("L")` semantics): a single-channel grayscale image suitable for PNG (or equivalent) download, with no neural-network weights required.

#### Scenario: Valid image becomes grayscale
- **WHEN** a client POSTs a valid image to sibling `/grayscale`
- **THEN** the response is a successful image payload in grayscale form equivalent to Pillow `convert("L")`

### Requirement: No new machine-learning weight formats
The sibling grayscale model MUST NOT introduce torch, ONNX, TensorFlow, or other learned-weight runtimes; the packaged artifact SHALL wrap the existing classical image conversion.

#### Scenario: Dependencies stay classical for grayscale
- **WHEN** the sibling environment is installed from its project dependency files
- **THEN** grayscale inference does not require a deep-learning framework beyond BentoML and Pillow already used for the lesson

### Requirement: Blur and resize remain direct classical paths
Sibling `/blur` and `/resize` MUST continue to apply Pillow filters/resizing directly in the service without requiring a BentoML model load for those endpoints.

#### Scenario: Blur does not require the grayscale model
- **WHEN** a client POSTs a valid image to sibling `/blur`
- **THEN** the service returns a blurred image without loading the grayscale picklable model as a prerequisite for that request

### Requirement: Model save is a documented offline step
The sibling SHALL document a non-interactive recipe to save/register the grayscale picklable model so a fresh machine can recreate the model artifact before serving.

#### Scenario: Fresh clone saves then serves grayscale
- **WHEN** a student runs the documented model-save recipe then starts the sibling service
- **THEN** `/grayscale` succeeds using the newly saved model artifact
