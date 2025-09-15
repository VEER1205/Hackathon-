from fastapi import APIRouter, Request, HTTPException, Depends, Cookie
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from jose import jwt, JWTError
from app.crud import user_crud
from app.config import settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["Auth"])

# --- OAuth Setup ---
config = Config(
    environ={
        "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
        "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
    }
)
oauth = OAuth(config)

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# --- JWT Token Helper ---
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload  # e.g., { "sub": "user@example.com", ... }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# --- Auth Routes ---
@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google auth error: {str(e)}")

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Google login failed")

    email = user_info.get("email")
    name = user_info.get("name")

    if not email:
        raise HTTPException(status_code=400, detail="Email not found in user info")

    # Store or retrieve user
    try:
        await user_crud.get_or_create_user(
            {
                "email": email,
                "name": name,  # Placeholder; not used
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB Error: {str(e)}")

    # Create JWT
    access_token = create_access_token(data={"sub": email})

    # Set HttpOnly cookie and redirect to frontend
    response = RedirectResponse(url="https://futuro-ai.web.app")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="None",  # Change this to allow cross-site requests
        max_age=3600,
    )
    return response


# --- Get Current User from Cookie ---
def get_current_user_from_cookie(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return verify_token(access_token)


@router.get("/me")
async def get_me(user=Depends(get_current_user_from_cookie)):
    email = user["sub"]
    db_user = await user_crud.get_user_by_email(email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "email": db_user["email"],
        "name": db_user["username"],
    }


# --- Logout (optional) ---
@router.post("/logout")
async def logout():
    response = RedirectResponse(url="https://futuro-ai.web.app")
    response.delete_cookie("access_token")
    return response
