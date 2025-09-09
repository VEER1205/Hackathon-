from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from app.routes import user_routes,gemini, auth_routes

app = FastAPI(title="PathFinder API")

# In dev, allow localhost & file origins (adjust for your setup)
origins = [
    "http://localhost:5500",     # VSCode Live Server
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # dev only; tighten for prod
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "super-secret-key"))

app.include_router(user_routes.router)
app.include_router(gemini.router,)
app.include_router(auth_routes.router)

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "PathFinder API"}
