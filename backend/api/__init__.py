from .map import router as map_router
from .rainfall import router as rainfall_router
from .soil import router as soil_router
from .crop import router as crop_router
from .simulation import router as simulation_router
from .roadmap import router as roadmap_router
from .chat import router as chat_router
from .baseline import router as baseline_router
from .spatial import router as spatial_router

__all__ = [
    "map_router",
    "rainfall_router",
    "soil_router",
    "crop_router",
    "simulation_router",
    "roadmap_router",
    "chat_router",
    "baseline_router",
    "spatial_router",
]