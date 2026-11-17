from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.api import spatial, simulation, chat, auth_router, crop_recommendation
from backend.core.config import get_settings, get_db
from backend.middleware.rate_limit import RateLimitMiddleware

settings = get_settings()

app = FastAPI(title="AgriBrain AI Digital Twin API", version="3.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Mount under /api/v1 only (single prefix)
app.include_router(spatial.router, prefix="/api/v1/spatial", tags=["Spatial"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(crop_recommendation.router, tags=["Crop Recommendation"])
app.include_router(auth_router.router, prefix="", tags=["Authentication"])

@app.get("/")
async def root():
    return {"status": "ok", "service": "AgriBrain Digital Twin Backend v3.0"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check with database connectivity verification."""
    db_status = "connected"
    db_error = None
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "disconnected"
        db_error = str(e)
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "AgriBrain Digital Twin Backend v3.0",
        "database": db_status,
        "database_error": db_error,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
