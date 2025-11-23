from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.dependencies import get_current_user, get_db
from app.schemas.auth import UserRead
from app.services import auth as auth_service
from app.services import orcid as orcid_service

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


@router.get("/login/orcid")
async def login_orcid():
    state = orcid_service.generate_state()
    url = orcid_service.build_authorize_url(state)
    return {"url": url, "state": state}


@router.get("/callback")
async def orcid_callback(code: str = "", state: str = "", db=Depends(get_db)):
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )
    try:
        token_data = await orcid_service.exchange_code_for_token(code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange code with ORCID",
        )

    orcid_id = token_data.get("orcid") or token_data.get("orcid-identifier", {}).get("path", "")
    name = token_data.get("name", "")

    try:
        record = await orcid_service.fetch_user_info(orcid_id, token_data["access_token"])
        person = record.get("person", {})
        given = person.get("name", {}).get("given-names", {}).get("value", "")
        family = person.get("name", {}).get("family-name", {}).get("value", "")
        if given or family:
            name = f"{given} {family}".strip()
        emails = person.get("emails", {}).get("email", [])
        email = emails[0].get("email") if emails else None
    except Exception:
        email = None

    user = await auth_service.get_or_create_user(db, orcid_id=orcid_id, name=name or orcid_id, email=email)
    jwt_token = auth_service.create_jwt(str(user.id), user.orcid_id)

    response = JSONResponse(content={"status": "ok"})
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )
    return response


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "logged out"})
    response.delete_cookie("access_token")
    return response
