from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse

from app.dependencies import get_current_user, get_db, optional_current_user
from app.schemas.file import FileList, FileRead
from app.services import files as files_service
from app.services import records as records_service
from app.services import storage

router = APIRouter(prefix="/records/{record_id}/files", tags=["files"])


@router.post("/", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    record_id: UUID,
    file: UploadFile,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    record = await records_service.get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your record")
    return await files_service.upload_file(db, record_id, file)


@router.get("/", response_model=FileList)
async def list_files(
    record_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    items, total = await files_service.list_files(db, record_id)
    return FileList(items=items, total=total)


@router.get("/{file_id}/download")
async def download_file(
    record_id: UUID,
    file_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    file_row = await files_service.get_file(db, file_id)
    if file_row is None or file_row.record_id != record_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    url = storage.get_presigned_download_url(file_row.minio_key)
    return RedirectResponse(url=url)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    record_id: UUID,
    file_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    file_row = await files_service.get_file(db, file_id)
    if file_row is None or file_row.record_id != record_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    record = await records_service.get_record(db, record_id)
    if record is None or record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your record")
    await files_service.delete_file(db, file_row)
