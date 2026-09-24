from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class ModelPrediction(TimestampMixin, Base):
    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id", ondelete="RESTRICT"), nullable=False, index=True)
    flow_id: Mapped[int] = mapped_column(ForeignKey("network_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    predicted_label: Mapped[str] = mapped_column(String(100), nullable=False)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    model_version = relationship("ModelVersion", back_populates="predictions")
    flow = relationship("NetworkFlow", back_populates="predictions")
    detections = relationship("Detection", back_populates="prediction")
