from fastapi import APIRouter

from .endpoints import health, history, interact, sessions

# Create the main v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(health.router)
router.include_router(sessions.router)
router.include_router(interact.router)
router.include_router(history.router)
