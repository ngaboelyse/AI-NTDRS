from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Device(TimestampMixin, Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_identifier: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), index=True, nullable=False)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_type: Mapped[str] = mapped_column(String(100), nullable=False)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activity_level: Mapped[str] = mapped_column(String(50), default="normal", nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    alert_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="online", nullable=False)

    flows = relationship("NetworkFlow", back_populates="device")
    alerts = relationship("Alert", back_populates="device")
    risk_scores = relationship("RiskScore", back_populates="device")
