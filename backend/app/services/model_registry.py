from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion


def ensure_demo_model_version(db: Session) -> ModelVersion:
    version = db.scalar(select(ModelVersion).where(ModelVersion.version == 'demo-heuristic-v1'))
    if version is not None:
        return version

    version = ModelVersion(
        model_name='Heuristic Demo Model',
        version='demo-heuristic-v1',
        algorithm='Rule-based risk scoring fallback',
        dataset_name='Demo traffic scenarios',
        training_started_at=datetime.now(timezone.utc),
        training_completed_at=datetime.now(timezone.utc),
        artifact_path=None,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def ensure_trained_demo_model_version(db: Session) -> ModelVersion:
    version = db.scalar(select(ModelVersion).where(ModelVersion.version == 'synthetic-rf-demo-v1'))
    if version is not None:
        return version

    now = datetime.now(timezone.utc)
    version = ModelVersion(
        model_name='Synthetic Flow Threat Classifier',
        version='synthetic-rf-demo-v1',
        algorithm='Random Forest classifier',
        dataset_name='Generated synthetic labeled flow scenarios',
        training_started_at=now,
        training_completed_at=now,
        artifact_path='ml/artifacts/random_forest.joblib',
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version
