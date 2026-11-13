from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from backend.core.config import settings
from backend.api import (
    map_router,
    rainfall_router,
    soil_router,
    crop_router,
    simulation_router,
    roadmap_router,
    chat,
    baseline,
    spatial
)
from backend.api import crop_recommendation


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting AgriSim Backend...")
    yield
    # Shutdown
    print("Shutting down AgriSim Backend...")


app = FastAPI(
    title="AgriSim API",
    description="Agricultural Simulation and Recommendation System for Indian Farmers",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(map_router)
app.include_router(rainfall_router)
app.include_router(soil_router)
app.include_router(crop_router)
app.include_router(crop_recommendation.router)
app.include_router(simulation_router)
app.include_router(roadmap_router)
app.include_router(chat.router)
app.include_router(baseline.router)
app.include_router(spatial.router)


@app.get("/")
async def root():
    return {
        "message": "AgriSim API - Agricultural Simulation System",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
