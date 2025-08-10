import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")


def is_oidc_enabled() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)


oauth = OAuth()
if is_oidc_enabled():
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        client_kwargs={"scope": "openid email profile"},
    )


@router.get("/auth/config")
def auth_config():
    return {"enabled": is_oidc_enabled()}


@router.get("/auth/login")
async def login(request: Request):
    if not is_oidc_enabled():
        # Demo mode: set a demo session
        request.session["user"] = {"mode": "demo"}
        return JSONResponse({"demo": True})
    redirect_uri = REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    if not is_oidc_enabled():
        raise HTTPException(status_code=400, detail="OIDC not enabled")
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session["user"] = {"sub": user.get("sub"), "email": user.get("email"), "name": user.get("name")}
    return RedirectResponse(url="/")


@router.post("/auth/logout")
def logout(request: Request):
    request.session.pop("user", None)
    return {"ok": True}