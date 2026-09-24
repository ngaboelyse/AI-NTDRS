from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class ResponseAction(TimestampMixin, Base):
    __tablename__ = "response_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=True, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    result: Mapped[str] = mapped_column(String(100), nullable=False)

    incident = relationship("Incident", back_populates="response_actions")
