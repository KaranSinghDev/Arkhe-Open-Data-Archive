from uuid import UUID, uuid4
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.record import Record
from app.schemas.record import RecordCreate, RecordUpdate


async def create_record(db: AsyncSession, payload: RecordCreate, user_id: UUID) -> Record:
    record = Record(
        id=uuid4(),
        user_id=user_id,
        **payload.model_dump(),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_record(db: AsyncSession, record_id: UUID) -> Record | None:
    result = await db.execute(select(Record).where(Record.id == record_id))
    return result.scalar_one_or_none()


async def list_records(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 20,
    user_id: UUID | None = None,
) -> tuple[list[Record], int]:
    q = select(Record)
    if user_id:
        q = q.where(Record.user_id == user_id)
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar_one()
    records = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(records), total


async def update_record(db: AsyncSession, record: Record, payload: RecordUpdate) -> Record:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    record.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(record)
    return record


async def delete_record(db: AsyncSession, record: Record) -> None:
    await db.delete(record)
    await db.commit()
