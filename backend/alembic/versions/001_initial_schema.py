"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-06-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("orcid_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("email", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("orcid_id", name="uq_users_orcid_id"),
    )
    op.create_index("ix_users_orcid_id", "users", ["orcid_id"], unique=True)

    op.create_table(
        "records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("doi", sa.String(128), nullable=True),
        sa.Column("record_type", sa.String(32), nullable=False),
        sa.Column("experiment", sa.String(64), nullable=True),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("license", sa.String(64), nullable=False, server_default="CC-BY-4.0"),
        sa.Column("keywords", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("doi", name="uq_records_doi"),
    )
    op.create_index("ix_records_user_id", "records", ["user_id"])
    op.create_index("ix_records_status", "records", ["status"])
    op.create_index("ix_records_experiment", "records", ["experiment"])

    op.create_table(
        "authors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("orcid", sa.String(64), nullable=True),
        sa.Column("affiliation", sa.String(512), nullable=True),
    )

    op.create_table(
        "record_authors",
        sa.Column("record_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("records.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("author_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("record_id", "author_id", name="uq_record_author"),
    )

    op.create_table(
        "files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.BigInteger, nullable=True),
        sa.Column("minio_key", sa.String(1024), nullable=False),
        sa.Column("parsed_metadata", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("minio_key", name="uq_files_minio_key"),
    )
    op.create_index("ix_files_record_id", "files", ["record_id"])


def downgrade() -> None:
    op.drop_table("files")
    op.drop_table("record_authors")
    op.drop_table("authors")
    op.drop_table("records")
    op.drop_table("users")
