"""
Model inference service for threat detection and risk scoring.
Provides unified interface for both anomaly detection and classification models.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    """Result from model inference."""
    predicted_label: str
    anomaly_score: float
    confidence: Optional[float]
    explanation: str
    model_name: str


class ModelInferenceService:
    """Service for loading and using trained ML models."""
    
    def __init__(self, artifact_dir: Optional[Path] = None):
        """
        Initialize inference service.
        
        Args:
            artifact_dir: Directory containing trained model artifacts
        """
        # Resolve from this file so model loading works whether uvicorn is
        # started in the repository root or from the backend directory.
        project_root = Path(__file__).resolve().parents[3]
        self.artifact_dir = artifact_dir or project_root / "ml" / "artifacts"
        self._isolation_forest: Optional[IsolationForest] = None
        self._isolation_pipeline = None
        self._random_forest: Optional[RandomForestClassifier] = None
        self._random_forest_pipeline = None
        self._model_loaded = False
    
    def load_models(self) -> bool:
        """
        Load trained models from disk.
        
        Returns:
            True if at least one model loaded successfully, False otherwise
        """
        try:
            isolation_model_path = self.artifact_dir / "isolation_forest.joblib"
            isolation_pipeline_path = self.artifact_dir / "isolation_forest_pipeline.joblib"
            
            if isolation_model_path.exists() and isolation_pipeline_path.exists():
                try:
                    self._isolation_forest = joblib.load(isolation_model_path)
                    self._isolation_pipeline = joblib.load(isolation_pipeline_path)
                    logger.info("Loaded Isolation Forest model successfully")
                except Exception as e:
                    logger.warning(f"Failed to load Isolation Forest: {e}")
        except Exception as e:
            logger.warning(f"Error checking Isolation Forest artifacts: {e}")
        
        try:
            rf_model_path = self.artifact_dir / "random_forest.joblib"
            rf_pipeline_path = self.artifact_dir / "random_forest_pipeline.joblib"
            
            if rf_model_path.exists() and rf_pipeline_path.exists():
                try:
                    self._random_forest = joblib.load(rf_model_path)
                    self._random_forest_pipeline = joblib.load(rf_pipeline_path)
                    logger.info("Loaded Random Forest model successfully")
                except Exception as e:
                    logger.warning(f"Failed to load Random Forest: {e}")
        except Exception as e:
            logger.warning(f"Error checking Random Forest artifacts: {e}")
        
        self._model_loaded = (
            self._isolation_forest is not None 
            or self._random_forest is not None
        )
        return self._model_loaded
    
    def detect_anomaly(self, flow_features: pd.DataFrame) -> InferenceResult:
        """
        Detect anomalies in flow data using Isolation Forest.
        
        Args:
            flow_features: DataFrame with flow features
            
        Returns:
            InferenceResult with anomaly detection output
        """
        if self._isolation_forest is None:
            return InferenceResult(
                predicted_label="Unknown",
                anomaly_score=0.0,
                confidence=None,
                explanation="No anomaly detection model loaded",
                model_name="None"
            )
        
        try:
            transformed = self._isolation_pipeline.transform(flow_features)
            prediction = self._isolation_forest.predict(transformed)[0]
            anomaly_score = -self._isolation_forest.score_samples(transformed)[0]
            
            # Normalize score to 0-1 range
            normalized_score = min(1.0, max(0.0, anomaly_score / 0.5))
            
            label = "Anomalous" if prediction == -1 else "Normal"
            # An anomaly score is not a calibrated probability.
            
            return InferenceResult(
                predicted_label=label,
                anomaly_score=normalized_score,
                confidence=None,
                explanation=f"Isolation Forest detected {'anomalous' if label == 'Anomalous' else 'normal'} behavior",
                model_name="IsolationForest"
            )
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return InferenceResult(
                predicted_label="Error",
                anomaly_score=0.0,
                confidence=None,
                explanation=f"Inference error: {str(e)}",
                model_name="IsolationForest"
            )
    
    def classify_threat(self, flow_features: pd.DataFrame) -> InferenceResult:
        """
        Classify threat type using Random Forest.
        
        Args:
            flow_features: DataFrame with flow features
            
        Returns:
            InferenceResult with threat classification
        """
        if self._random_forest is None:
            return InferenceResult(
                predicted_label="Unknown",
                anomaly_score=0.0,
                confidence=None,
                explanation="No classification model loaded",
                model_name="None"
            )
        
        try:
            transformed = self._random_forest_pipeline.transform(flow_features)
            prediction = self._random_forest.predict(transformed)[0]
            class_votes = self._random_forest.predict_proba(transformed)[0]
            classes = list(self._random_forest.classes_)
            if "Normal" in classes:
                threat_vote_score = 1.0 - float(class_votes[classes.index("Normal")])
            else:
                threat_vote_score = float(max(class_votes))
            # Relative tree votes are not calibrated probabilities.
            return InferenceResult(
                predicted_label=str(prediction),
                anomaly_score=min(1.0, max(0.0, threat_vote_score)),
                confidence=None,
                explanation=f"Random Forest classified as {prediction}; relative threat vote score {threat_vote_score:.2f} (uncalibrated)",
                model_name="RandomForest"
            )
        except Exception as e:
            logger.error(f"Error in threat classification: {e}")
            return InferenceResult(
                predicted_label="Error",
                anomaly_score=0.0,
                confidence=None,
                explanation=f"Classification error: {str(e)}",
                model_name="RandomForest"
            )
    
    def infer(self, flow_features: pd.DataFrame) -> InferenceResult:
        """
        Run inference using available models (anomaly detection preferred).
        
        Args:
            flow_features: DataFrame with flow features
            
        Returns:
            InferenceResult from the best available model
        """
        # Prefer anomaly detection if available
        if self._isolation_forest is not None:
            return self.detect_anomaly(flow_features)
        elif self._random_forest is not None:
            return self.classify_threat(flow_features)
        else:
            return InferenceResult(
                predicted_label="Unknown",
                anomaly_score=0.0,
                confidence=None,
                explanation="No ML models available",
                model_name="None"
            )
    
    def is_ready(self) -> bool:
        """Check if inference service is ready to use."""
        return self._model_loaded


# Global inference service instance
_inference_service: Optional[ModelInferenceService] = None


def get_inference_service() -> ModelInferenceService:
    """Get or create global inference service."""
    global _inference_service
    if _inference_service is None:
        _inference_service = ModelInferenceService()
        if settings.flow_model_enabled:
            _inference_service.load_models()
    return _inference_service
