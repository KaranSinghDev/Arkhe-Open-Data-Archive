from app.models.file import File
from app.models.record import Record


def trigger_file_parse(file_row: File) -> None:
    from app.workers.tasks.parse_file import parse_file
    parse_file.delay(
        str(file_row.id),
        file_row.minio_key,
        file_row.content_type,
        file_row.filename,
    )


def trigger_record_index(record: Record) -> None:
    from app.workers.tasks.index_record import index_record
    index_record.delay(str(record.id))


def trigger_record_deindex(record_id: str) -> None:
    from app.workers.tasks.index_record import deindex_record
    deindex_record.delay(record_id)
