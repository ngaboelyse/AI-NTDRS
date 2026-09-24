from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Detection(TimestampMixin, Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    flow_id: Mapped[int] = mapped_column(ForeignKey("network_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("model_predictions.id", ondelete="CASCADE"), nullable=False, index=True)
    threat_category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    device = relationship("Device")
    flow = relationship("NetworkFlow", back_populates="detections")
    prediction = relationship("ModelPrediction", back_populates="detections")
    alerts = relationship("Alert", back_populates="detection")
