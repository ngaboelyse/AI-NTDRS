from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SensorEventReceipt(Base):
    """Idempotency receipt for authenticated external sensor events."""

    __tablename__ = "sensor_event_receipts"

    event_key: Mapped[str] = mapped_column(String(180), primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
