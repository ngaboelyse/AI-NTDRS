# ML Pipeline

This package contains the first ML implementation slice for AI-NTDRS.

## Scope

- Flow preprocessing
- Baseline anomaly detection
- Supervised classification baseline
- Evaluation metrics
- Explainability helpers

## Demo training

Run `python -m ml.training.train_demo` from the repository root to generate a
reproducible synthetic flow dataset, compare five Random Forest configurations,
and save the best classifier and its preprocessing pipeline under `ml/artifacts`.
The validation metrics are recorded in `ml/artifacts/training_metrics.json`.
These generated examples exercise the training and inference pipeline only;
they do not represent real network traffic or establish field accuracy. For
operational training, provide representative, reviewed, labeled flow data.

## Design Notes

- Prefer flow metadata over payload content.
- Use classical tabular ML first for explainability and deployment simplicity.
- Keep artifacts versioned and reproducible.

## Conversational assistant fine-tuning

For the separate human-interaction Copilot, see
[`training/COPILOT_FINE_TUNING.md`](training/COPILOT_FINE_TUNING.md). Its SFT
workflow uses reviewed conversation examples and a GPU; it is separate from the
network-flow classifier above.
