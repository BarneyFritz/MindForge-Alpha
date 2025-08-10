from fastapi import APIRouter, Depends, Request, HTTPException
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import get_settings
from app.auth.google_auth import GoogleAuthService
from app.utils.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

google_service = GoogleAuthService(
    client_id=settings.google_client_id or "", client_secret=settings.google_client_secret or ""
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await google_service.create_auth_url(request, str(redirect_uri))

@router.get("/callback")
async def auth_callback(request: Request):
    try:
        user_info = await google_service.verify_token(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    token = create_access_token({"sub": user_info.email, "name": user_info.name})
    response = RedirectResponse(url=f"{settings.frontend_origin}/auth/success?token={token}")
    return response