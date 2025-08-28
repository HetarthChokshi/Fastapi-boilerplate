from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.database import get_db
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI(
    title="FastAPI JWT Auth Boilerplate",
    description="A production-ready FastAPI boilerplate with JWT authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])

@app.get("/")
async def root():
    return {"message": "FastAPI JWT Auth Boilerplate"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
