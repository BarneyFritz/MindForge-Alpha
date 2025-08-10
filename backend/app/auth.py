from __future__ import annotations
from typing import Optional
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from .config import get_settings

_settings = get_settings()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=_settings.GOOGLE_CLIENT_ID or "",
    client_secret=_settings.GOOGLE_CLIENT_SECRET or "",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

SESSION_USER_KEY = "user"

def get_user_from_session(request: Request) -> Optional[dict]:
    return request.session.get(SESSION_USER_KEY)

def set_user_in_session(request: Request, user: dict) -> None:
    request.session[SESSION_USER_KEY] = user

def clear_user_session(request: Request) -> None:
    if SESSION_USER_KEY in request.session:
        del request.session[SESSION_USER_KEY]