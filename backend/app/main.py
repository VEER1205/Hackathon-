from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from app.config import settings
from app.routes import user_routes,gemini, auth_routes
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException



app = FastAPI(title="PathFinder API")

# In dev, allow localhost & file origins (adjust for your setup)
origins = [
    "http://localhost:5500",     # VSCode Live Server
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://futuro-ai.web.app",
    "https://hackwave-sxj1.onrender.com"# dev only; tighten for prod
]

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_routes.router)
app.include_router(gemini.router,)
app.include_router(auth_routes.router)



@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "PathFinder API","version": "1.1.0"}

def wants_html(request: Request):
    return "text/html" in request.headers.get("accept", "")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if wants_html(request):
        return RedirectResponse("https://futuro-ai.web.app/error", status_code=exc.status_code)
    return JSONResponse({"error": "Something went wrong 😞"}, status_code=exc.status_code)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    if wants_html(request):
        return RedirectResponse("https://futuro-ai.web.app/error", status_code=500)
    return JSONResponse({"error": "Something went wrong 😞"}, status_code=500)

@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
async def health_check():
    return {"status": "ok"}