import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, func, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Record(Base):
    __tablename__ = "records"
    __table_args__ = (
        Index("ix_records_user_id", "user_id"),
        Index("ix_records_status", "status"),
        Index("ix_records_experiment", "experiment"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    record_type: Mapped[str] = mapped_column(String(32), nullable=False)  # dataset | publication
    experiment: Mapped[str | None] = mapped_column(String(64), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    license: Mapped[str] = mapped_column(String(64), nullable=False, default="CC-BY-4.0")
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )  # pending | processing | indexed | error
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="records")  # type: ignore[name-defined]  # noqa: F821
    files: Mapped[list["File"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "File", back_populates="record", cascade="all, delete-orphan"
    )
    record_authors: Mapped[list["RecordAuthor"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "RecordAuthor", back_populates="record", cascade="all, delete-orphan",
        order_by="RecordAuthor.author_order"
    )
