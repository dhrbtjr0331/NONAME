import sys
import os

# Add the current service directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.dirname(current_dir)
sys.path.insert(0, service_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import rfqs, quotes
from app.config.database import engine
from app.models.rfq import Base as RFQBase
from app.models.quote import Base as QuoteBase

app = FastAPI(title="Quote Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rfqs.router)
app.include_router(quotes.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(RFQBase.metadata.create_all)
        await conn.run_sync(QuoteBase.metadata.create_all)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quote-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)