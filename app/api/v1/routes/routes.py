from fastapi import APIRouter

from app.api.v1.routes.colorize import router as colorize_router
from app.api.v1.routes.stats import router as stats_router

router = APIRouter()

# Include routers
router.include_router(colorize_router, prefix="/colorize", tags=["Colorize"])
router.include_router(stats_router, prefix="/stats", tags=["Stats"])
