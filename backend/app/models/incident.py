from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin

incident_alerts = Table(
    "incident_alerts",
    Base.metadata,
    Column("incident_id", ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("alert_id", ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True),
)


class Incident(TimestampMixin, Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="NEW", nullable=False)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    assigned_analyst_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assigned_analyst = relationship("User")
    alerts = relationship("Alert", secondary=incident_alerts, back_populates="incidents")
    response_actions = relationship("ResponseAction", back_populates="incident")
    risk_scores = relationship("RiskScore", back_populates="incident")
