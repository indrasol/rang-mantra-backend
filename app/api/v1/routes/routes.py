from fastapi import APIRouter

from app.api.v1.routes.colorize import router as colorize_router

router = APIRouter()

# Include routers
router.include_router(colorize_router, prefix="/colorize", tags=["Colorize"])
