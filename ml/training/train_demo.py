"""Train a demo threat classifier on reproducible synthetic flow scenarios.

The generated data is for pipeline development and UI demonstrations only. It
is not a substitute for labeled traffic collected in an authorized environment.
Run from the repository root with ``python -m ml.training.train_demo``.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from ml.preprocessing.pipeline import FlowPreprocessor


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "ml" / "datasets"
ARTIFACT_DIR = ROOT / "ml" / "artifacts"
TARGET = "threat_label"
LABELS = ("Normal", "Port Scan", "Brute Force", "DDoS", "Data Exfiltration")


def make_synthetic_flows(samples_per_class: int = 500, seed: int = 2026) -> pd.DataFrame:
    """Create scenario-shaped metadata without capturing or replaying traffic."""
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []
    source_pool = [f"10.20.{net}.{host}" for net in range(1, 5) for host in (10, 20, 30, 40)]
    destination_pool = [f"198.51.100.{host}" for host in range(10, 30)]

    for label in LABELS:
        for _ in range(samples_per_class):
            device_id = str(rng.integers(1, 13))
            source_ip = str(rng.choice(source_pool))
            destination_ip = str(rng.choice(destination_pool))
            direction = str(rng.choice(["outbound", "inbound"], p=[0.85, 0.15]))
            protocol = str(rng.choice(["TCP", "UDP", "ICMP"], p=[0.72, 0.24, 0.04]))
            source_port = int(rng.integers(1024, 65536))

            if label == "Normal":
                destination_port = int(rng.choice([53, 80, 123, 443, 8080, 8443, rng.integers(1024, 65536)]))
                packet_count = int(rng.integers(15, 1800))
                byte_count = int(rng.integers(500, 1_200_000))
                flow_duration = float(rng.uniform(0.2, 360))
                connection_count = int(rng.integers(1, 9))
                request_frequency = float(rng.uniform(0.05, 14))
                failed_connection_count = int(rng.choice([0, 0, 0, 1, 2]))
            elif label == "Port Scan":
                protocol = "TCP"
                destination_port = int(rng.integers(1, 2049))
                packet_count = int(rng.integers(1, 30))
                byte_count = int(rng.integers(40, 18_000))
                flow_duration = float(rng.uniform(0.01, 12))
                connection_count = int(rng.integers(18, 450))
                request_frequency = float(rng.uniform(5, 100))
                failed_connection_count = int(rng.integers(8, 400))
            elif label == "Brute Force":
                protocol = "TCP"
                destination_port = int(rng.choice([21, 22, 23, 3389]))
                packet_count = int(rng.integers(2, 160))
                byte_count = int(rng.integers(100, 95_000))
                flow_duration = float(rng.uniform(0.1, 80))
                connection_count = int(rng.integers(8, 180))
                request_frequency = float(rng.uniform(1, 35))
                failed_connection_count = int(rng.integers(6, 160))
            elif label == "DDoS":
                protocol = str(rng.choice(["TCP", "UDP"], p=[0.45, 0.55]))
                direction = "inbound"
                destination_port = int(rng.choice([53, 80, 443, 8080, 8443]))
                packet_count = int(rng.integers(900, 30_000))
                byte_count = int(rng.integers(80_000, 25_000_000))
                flow_duration = float(rng.uniform(0.05, 90))
                connection_count = int(rng.integers(80, 1800))
                request_frequency = float(rng.uniform(35, 900))
                failed_connection_count = int(rng.integers(0, 80))
            else:  # Data Exfiltration
                direction = "outbound"
                destination_port = int(rng.choice([443, 8443, 22, 8080]))
                packet_count = int(rng.integers(150, 12_000))
                byte_count = int(rng.integers(2_000_000, 80_000_000))
                flow_duration = float(rng.uniform(20, 2400))
                connection_count = int(rng.integers(1, 24))
                request_frequency = float(rng.uniform(0.1, 25))
                failed_connection_count = int(rng.integers(0, 5))

            records.append({
                "packet_count": packet_count,
                "byte_count": byte_count,
                "flow_duration": flow_duration,
                "connection_count": connection_count,
                "request_frequency": request_frequency,
                "failed_connection_count": failed_connection_count,
                "source_port": source_port,
                "destination_port": destination_port,
                "protocol": protocol,
                "direction": direction,
                "device_id": device_id,
                "source_ip": source_ip,
                "destination_ip": destination_ip,
                TARGET: label,
            })

    return pd.DataFrame.from_records(records).sample(frac=1, random_state=seed).reset_index(drop=True)


def train(attempts: int = 5, samples_per_class: int = 500, seed: int = 2026) -> dict[str, object]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    frame = make_synthetic_flows(samples_per_class=samples_per_class, seed=seed)
    dataset_path = DATA_DIR / "synthetic_labeled_flows.csv"
    frame.to_csv(dataset_path, index=False)

    preprocessor = FlowPreprocessor()
    validated = preprocessor.validate(frame)
    labels = validated.pop(TARGET)
    x_train, x_test, y_train, y_test = train_test_split(
        validated,
        labels,
        test_size=0.2,
        random_state=seed,
        stratify=labels,
    )

    candidates = [
        {"n_estimators": 120, "max_depth": 12, "min_samples_leaf": 2},
        {"n_estimators": 180, "max_depth": 16, "min_samples_leaf": 2},
        {"n_estimators": 240, "max_depth": None, "min_samples_leaf": 1},
        {"n_estimators": 320, "max_depth": 20, "min_samples_leaf": 1},
        {"n_estimators": 400, "max_depth": None, "min_samples_leaf": 2},
    ][:attempts]
    if not candidates:
        raise ValueError("attempts must be at least 1")

    best_model = None
    best_pipeline = None
    best_parameters = None
    best_score = -1.0
    attempt_results: list[dict[str, object]] = []

    for attempt_number, parameters in enumerate(candidates, start=1):
        pipeline = preprocessor.build_pipeline()
        transformed_train = pipeline.fit_transform(x_train)
        model = RandomForestClassifier(
            **parameters,
            class_weight="balanced",
            random_state=seed + attempt_number,
            n_jobs=-1,
        )
        model.fit(transformed_train, y_train)
        predictions = model.predict(pipeline.transform(x_test))
        score = float(f1_score(y_test, predictions, average="weighted"))
        attempt_results.append({
            "attempt": attempt_number,
            "parameters": parameters,
            "weighted_f1": score,
        })
        print(f"Attempt {attempt_number}/{len(candidates)}: weighted F1={score:.4f} parameters={parameters}")
        if score > best_score:
            best_score = score
            best_model = model
            best_pipeline = pipeline
            best_parameters = parameters

    assert best_model is not None and best_pipeline is not None and best_parameters is not None
    model_path = ARTIFACT_DIR / "random_forest.joblib"
    pipeline_path = ARTIFACT_DIR / "random_forest_pipeline.joblib"
    joblib.dump(best_model, model_path)
    joblib.dump(best_pipeline, pipeline_path)

    predictions = best_model.predict(best_pipeline.transform(x_test))
    report = {
        "training_type": "synthetic_demo_only",
        "random_seed": seed,
        "rows": len(frame),
        "training_rows": len(x_train),
        "validation_rows": len(x_test),
        "class_counts": {str(key): int(value) for key, value in frame[TARGET].value_counts().items()},
        "attempts": attempt_results,
        "selected_parameters": best_parameters,
        "validation_accuracy": float(accuracy_score(y_test, predictions)),
        "validation_weighted_f1": best_score,
        "classification_report": classification_report(y_test, predictions, output_dict=True, zero_division=0),
        "confusion_matrix_labels": list(best_model.classes_),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=best_model.classes_).tolist(),
        "model_path": str(model_path.relative_to(ROOT)),
        "pipeline_path": str(pipeline_path.relative_to(ROOT)),
        "dataset_path": str(dataset_path.relative_to(ROOT)),
        "warning": "Synthetic scenario metrics are not evidence of real-world detection performance.",
    }
    metrics_path = ARTIFACT_DIR / "training_metrics.json"
    metrics_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Selected validation weighted F1={best_score:.4f}; saved artifacts to {ARTIFACT_DIR}")
    return report


if __name__ == "__main__":
    train()
