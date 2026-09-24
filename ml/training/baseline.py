from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split

from ml.preprocessing.pipeline import FlowPreprocessor


@dataclass
class TrainingArtifact:
    model_name: str
    artifact_path: Path
    feature_pipeline_path: Path


def train_anomaly_model(frame: pd.DataFrame, artifact_dir: Path) -> TrainingArtifact:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    preprocessor = FlowPreprocessor()
    pipeline = preprocessor.build_pipeline()
    features = preprocessor.validate(frame)
    transformed = pipeline.fit_transform(features)

    model = IsolationForest(n_estimators=200, contamination='auto', random_state=42)
    model.fit(transformed)

    model_path = artifact_dir / 'isolation_forest.joblib'
    pipeline_path = artifact_dir / 'isolation_forest_pipeline.joblib'
    joblib.dump(model, model_path)
    joblib.dump(pipeline, pipeline_path)

    return TrainingArtifact(
        model_name='IsolationForest',
        artifact_path=model_path,
        feature_pipeline_path=pipeline_path,
    )


def train_classification_model(frame: pd.DataFrame, target_column: str, artifact_dir: Path) -> TrainingArtifact:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    preprocessor = FlowPreprocessor()
    pipeline = preprocessor.build_pipeline()

    features = preprocessor.validate(frame)
    labels = features.pop(target_column)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels if labels.nunique() > 1 else None,
    )

    transformed_train = pipeline.fit_transform(x_train)
    model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
    model.fit(transformed_train, y_train)

    model_path = artifact_dir / 'random_forest.joblib'
    pipeline_path = artifact_dir / 'random_forest_pipeline.joblib'
    joblib.dump(model, model_path)
    joblib.dump(pipeline, pipeline_path)

    return TrainingArtifact(
        model_name='RandomForestClassifier',
        artifact_path=model_path,
        feature_pipeline_path=pipeline_path,
    )
