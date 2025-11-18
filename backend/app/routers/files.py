from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.dependencies import get_current_user, get_db, optional_current_user
from app.schemas.file import FileList, FileRead

router = APIRouter(prefix="/records/{record_id}/files", tags=["files"])


@router.post("/", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    record_id: UUID,
    file: UploadFile,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/", response_model=FileList)
async def list_files(
    record_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    return FileList(items=[], total=0)


@router.get("/{file_id}/download")
async def download_file(
    record_id: UUID,
    file_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    record_id: UUID,
    file_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
