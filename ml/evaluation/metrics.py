from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class EvaluationReport:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    false_negative_rate: float
    roc_auc: float | None
    confusion_matrix: list[list[int]]


def evaluate_classification(y_true, y_pred, y_score=None) -> EvaluationReport:
    matrix = confusion_matrix(y_true, y_pred)
    if matrix.size == 4:
        tn, fp, fn, tp = matrix.ravel()
        false_positive_rate = fp / (fp + tn) if (fp + tn) else 0.0
        false_negative_rate = fn / (fn + tp) if (fn + tp) else 0.0
    else:
        false_positive_rate = 0.0
        false_negative_rate = 0.0

    roc_auc = None
    if y_score is not None:
        try:
            roc_auc = float(roc_auc_score(y_true, y_score))
        except ValueError:
            roc_auc = None

    return EvaluationReport(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
        recall=float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
        f1_score=float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
        false_positive_rate=float(false_positive_rate),
        false_negative_rate=float(false_negative_rate),
        roc_auc=roc_auc,
        confusion_matrix=matrix.tolist(),
    )
