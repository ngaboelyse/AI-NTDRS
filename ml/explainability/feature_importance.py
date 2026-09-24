from __future__ import annotations

from typing import Any


def top_feature_importance(model: Any, feature_names: list[str], limit: int = 10) -> list[dict[str, float]]:
    importances = getattr(model, 'feature_importances_', None)
    if importances is None:
        return []

    ranked = sorted(zip(feature_names, importances), key=lambda item: item[1], reverse=True)
    return [
        {'feature': feature, 'importance': float(score)}
        for feature, score in ranked[:limit]
    ]
