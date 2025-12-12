from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.dependencies import Pagination, get_current_user, get_db, optional_current_user
from app.schemas.record import RecordCreate, RecordList, RecordRead, RecordUpdate
from app.services import records as records_service
from app.services import tasks as tasks_service

_LICENSE_URLS = {
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "MIT": "https://opensource.org/licenses/MIT",
}

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
async def create_record(
    payload: RecordCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    return await records_service.create_record(db, payload, current_user.id)


@router.get("/", response_model=RecordList)
async def list_records(
    pagination: Pagination = Depends(),
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    items, total = await records_service.list_records(db, offset=pagination.offset, limit=pagination.size)
    return RecordList(items=items, total=total, page=pagination.page, size=pagination.size)


@router.get("/{record_id}", response_model=RecordRead)
async def get_record(
    record_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    record = await records_service.get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.patch("/{record_id}", response_model=RecordRead)
async def update_record(
    record_id: UUID,
    payload: RecordUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    record = await records_service.get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your record")
    was_pending = record.status != "published"
    updated = await records_service.update_record(db, record, payload)
    if was_pending and updated.status == "published":
        tasks_service.trigger_record_index(updated)
    return updated


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    record = await records_service.get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your record")
    tasks_service.trigger_record_deindex(str(record.id))
    await records_service.delete_record(db, record)


@router.get("/{record_id}/metadata.json")
async def fair_metadata(
    record_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    record = await records_service.get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    doc = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "identifier": f"doi:{record.doi}" if record.doi else str(record.id),
        "name": record.title,
        "description": record.description,
        "keywords": record.keywords or [],
        "license": _LICENSE_URLS.get(record.license, record.license),
        "dateCreated": record.created_at.isoformat(),
        "dateModified": record.updated_at.isoformat(),
        "isAccessibleForFree": True,
    }
    return JSONResponse(content=doc, media_type="application/ld+json")
