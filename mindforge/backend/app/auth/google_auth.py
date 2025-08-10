from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel

class UserInfo(BaseModel):
    email: str
    name: str | None = None
    picture: str | None = None

class GoogleAuthService:
    def __init__(self, client_id: str, client_secret: str):
        self.oauth = OAuth()
        self.oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
            client_kwargs={'scope': 'openid email profile'}
        )

    async def create_auth_url(self, request, redirect_uri: str):
        return await self.oauth.google.authorize_redirect(request, redirect_uri)

    async def verify_token(self, request) -> UserInfo:
        token = await self.oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        return UserInfo(
            email=user_info['email'],
            name=user_info.get('name'),
            picture=user_info.get('picture')
        )