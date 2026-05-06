import uuid

from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    orcid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    affiliation: Mapped[str | None] = mapped_column(String(512), nullable=True)

    record_authors: Mapped[list["RecordAuthor"]] = relationship("RecordAuthor", back_populates="author")


class RecordAuthor(Base):
    __tablename__ = "record_authors"
    __table_args__ = (
        UniqueConstraint("record_id", "author_id", name="uq_record_author"),
    )

    record_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("records.id", ondelete="CASCADE"), primary_key=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
    )
    author_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    record: Mapped["Record"] = relationship("Record", back_populates="record_authors")  # type: ignore[name-defined]  # noqa: F821
    author: Mapped["Author"] = relationship("Author", back_populates="record_authors")
