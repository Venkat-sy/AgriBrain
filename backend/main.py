from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import spatial, simulation, chat

app = FastAPI(title="AgriBrain AI Digital Twin API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount under both /api/v1 and /api to prevent 404 Not Found errors
app.include_router(spatial.router, prefix="/api/v1/spatial", tags=["Spatial"])
app.include_router(spatial.router, prefix="/api/spatial", tags=["Spatial-Fallback"])

app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation-Fallback"])

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat-Fallback"])

@app.get("/")
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "AgriBrain Digital Twin Backend v3.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
