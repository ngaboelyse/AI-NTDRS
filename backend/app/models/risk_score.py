from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class RiskScore(TimestampMixin, Base):
    __tablename__ = "risk_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int | None] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=True, index=True)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    contributing_factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    device = relationship("Device", back_populates="risk_scores")
    alert = relationship("Alert", back_populates="risk_scores")
    incident = relationship("Incident", back_populates="risk_scores")
