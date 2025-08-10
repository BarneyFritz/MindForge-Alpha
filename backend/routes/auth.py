import os
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:5173")

oauth = None
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


@router.get("/auth/status")
async def auth_status(request: Request):
    user = request.session.get("user") if hasattr(request, "session") else None
    return {"enabled": bool(oauth), "user": user}


@router.get("/auth/login")
async def login(request: Request):
    if not oauth:
        return JSONResponse({"enabled": False, "message": "Demo mode (no Google OAuth configured)"})
    redirect_uri = OAUTH_REDIRECT_URI.rstrip("/") + "/api/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    if not oauth:
        return RedirectResponse("/")
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    request.session["user"] = {"email": user_info.get("email"), "name": user_info.get("name")}
    return RedirectResponse("/")


@router.post("/auth/logout")
async def logout(request: Request):
    if hasattr(request, "session"):
        request.session.clear()
    return {"ok": True}