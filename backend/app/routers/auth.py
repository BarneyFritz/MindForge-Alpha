from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import oauth, get_user_from_session, set_user_in_session, clear_user_session
from ..config import get_settings
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

@router.get("/login")
async def login(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    redirect_uri = settings.OAUTH_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")
    # Upsert user
    user = db.query(User).filter(User.email == userinfo["email"]).first()
    if not user:
        user = User(email=userinfo["email"], name=userinfo.get("name"), picture=userinfo.get("picture"))
        db.add(user)
        db.commit()
        db.refresh(user)
    set_user_in_session(request, {"id": user.id, "email": user.email, "name": user.name, "picture": user.picture})
    return RedirectResponse(url="/")

@router.get("/me")
async def me(request: Request):
    user = get_user_from_session(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@router.post("/logout")
async def logout(request: Request):
    clear_user_session(request)
    return {"ok": True}

# Dev-only helper when OAuth not set
@router.get("/dev-login")
async def dev_login(request: Request, db: Session = Depends(get_db)):
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=400, detail="Use real OAuth when configured")
    email = "dev@example.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name="Dev User")
        db.add(user)
        db.commit()
        db.refresh(user)
    set_user_in_session(request, {"id": user.id, "email": user.email, "name": user.name})
    return {"ok": True}