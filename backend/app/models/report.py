from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Report(TimestampMixin, Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_title: Mapped[str] = mapped_column(String(255), nullable=False)
    incident_id: Mapped[int | None] = mapped_column(ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    generated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    export_format: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    incident = relationship("Incident")
    generated_by = relationship("User")
