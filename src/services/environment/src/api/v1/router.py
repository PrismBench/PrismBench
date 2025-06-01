from fastapi import APIRouter

from .endpoints import challenges, health

# Create the main v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(challenges.router)
router.include_router(health.router)
