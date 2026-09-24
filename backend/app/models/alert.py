from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    detection_id: Mapped[int] = mapped_column(ForeignKey("detections.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    protocol: Mapped[str] = mapped_column(String(20), nullable=False)
    threat_category: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    detection_reason: Mapped[str] = mapped_column(Text, nullable=False)
    model_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="NEW", nullable=False)
    assigned_analyst_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    analyst_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    detection = relationship("Detection", back_populates="alerts")
    device = relationship("Device", back_populates="alerts")
    assigned_analyst = relationship("User")
    risk_scores = relationship("RiskScore", back_populates="alert")
    incidents = relationship("Incident", secondary="incident_alerts", back_populates="alerts")
