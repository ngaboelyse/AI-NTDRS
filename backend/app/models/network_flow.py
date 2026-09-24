from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class NetworkFlow(TimestampMixin, Base):
    __tablename__ = "network_flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    source_ip: Mapped[str] = mapped_column(String(45), index=True, nullable=False)
    destination_ip: Mapped[str] = mapped_column(String(45), index=True, nullable=False)
    source_port: Mapped[int] = mapped_column(Integer, nullable=False)
    destination_port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(20), nullable=False)
    packet_count: Mapped[int] = mapped_column(Integer, nullable=False)
    byte_count: Mapped[int] = mapped_column(Integer, nullable=False)
    flow_duration: Mapped[float] = mapped_column(Float, nullable=False)
    connection_count: Mapped[int] = mapped_column(Integer, nullable=False)
    request_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    failed_connection_count: Mapped[int] = mapped_column(Integer, nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload_collected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    device = relationship("Device", back_populates="flows")
    predictions = relationship("ModelPrediction", back_populates="flow")
    detections = relationship("Detection", back_populates="flow")
