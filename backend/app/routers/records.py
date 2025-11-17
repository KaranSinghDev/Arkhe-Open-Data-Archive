from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import Pagination, get_current_user, get_db, optional_current_user
from app.schemas.record import RecordCreate, RecordList, RecordRead, RecordUpdate

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
async def create_record(
    payload: RecordCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/", response_model=RecordList)
async def list_records(
    pagination: Pagination = Depends(),
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    return RecordList(items=[], total=0, page=pagination.page, size=pagination.size)


@router.get("/{record_id}", response_model=RecordRead)
async def get_record(
    record_id: UUID,
    current_user=Depends(optional_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")


@router.patch("/{record_id}", response_model=RecordRead)
async def update_record(
    record_id: UUID,
    payload: RecordUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_id: UUID,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
