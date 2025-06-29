from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.config.database import create_tables
from app.routers import auth, users, companies, rfqs, quotes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(rfqs.router)
app.include_router(quotes.router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "core-api",
        "environment": settings.ENVIRONMENT
    }

@app.get("/")
async def root():
    return {
        "message": "Marketplace Core API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)