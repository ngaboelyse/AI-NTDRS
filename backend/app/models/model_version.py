from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class ModelVersion(TimestampMixin, Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(200), nullable=False)
    training_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    training_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    artifact_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    predictions = relationship("ModelPrediction", back_populates="model_version")
