from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os
from app.crud import user_crud
from app.auth import create_access_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

config = Config(environ={
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
})
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# --- Login ---
@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# --- Callback ---
@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    try:
        # Exchange code for token
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google auth error: {str(e)}")

    # Get user info from token
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Google login failed")

    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in user info")

    # ✅ Store user in MongoDB
    try:
        await user_crud.get_or_create_user({
            "email": email,
            "name": name,
            "picture": picture,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

    # ✅ Generate JWT token
    access_token = create_access_token(data={"sub": email})

    # ✅ Redirect to frontend with token
    redirect_url = f"https://futuroai.vercel.app/?token={access_token}"
    return RedirectResponse(url=redirect_url)


