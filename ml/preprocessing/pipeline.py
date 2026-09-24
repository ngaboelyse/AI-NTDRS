from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC_FEATURES = [
    'packet_count',
    'byte_count',
    'flow_duration',
    'connection_count',
    'request_frequency',
    'failed_connection_count',
    'source_port',
    'destination_port',
]

CATEGORICAL_FEATURES = [
    'protocol',
    'direction',
    'device_id',
    'source_ip',
    'destination_ip',
]


def default_feature_columns() -> list[str]:
    return NUMERIC_FEATURES + CATEGORICAL_FEATURES


@dataclass
class FlowPreprocessor:
    numeric_features: list[str] = None
    categorical_features: list[str] = None

    def __post_init__(self) -> None:
        if self.numeric_features is None:
            self.numeric_features = NUMERIC_FEATURES.copy()
        if self.categorical_features is None:
            self.categorical_features = CATEGORICAL_FEATURES.copy()

    def build_pipeline(self) -> ColumnTransformer:
        numeric_pipeline = Pipeline(
            steps=[
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
            ]
        )

        categorical_pipeline = Pipeline(
            steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore')),
            ]
        )

        return ColumnTransformer(
            transformers=[
                ('numeric', numeric_pipeline, self.numeric_features),
                ('categorical', categorical_pipeline, self.categorical_features),
            ],
            remainder='drop',
        )

    def validate(self, frame: pd.DataFrame) -> pd.DataFrame:
        required = set(self.numeric_features + self.categorical_features)
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f'Missing required columns: {sorted(missing)}')
        return frame.copy()

    def transform(self, frame: pd.DataFrame) -> tuple[ColumnTransformer, pd.DataFrame]:
        validated = self.validate(frame)
        pipeline = self.build_pipeline()
        transformed = pipeline.fit_transform(validated)
        return pipeline, transformed
