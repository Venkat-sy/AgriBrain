from .map import router as map_router
from .rainfall import router as rainfall_router
from .soil import router as soil_router
from .crop import router as crop_router
from .simulation import router as simulation_router
from .roadmap import router as roadmap_router

__all__ = [
    "map_router",
    "rainfall_router",
    "soil_router",
    "crop_router",
    "simulation_router",
    "roadmap_router",
]