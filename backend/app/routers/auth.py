from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies import get_current_user
from app.schemas.auth import TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login/orcid")
async def login_orcid():
    return {"url": ""}


@router.get("/callback")
async def orcid_callback(code: str = "", state: str = ""):
    return {}


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "logged out"})
    response.delete_cookie("access_token")
    return response
