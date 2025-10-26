from fastapi import APIRouter

from .endpoints import health, sessions, tasks, trees

# Create the main v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(sessions.router)
router.include_router(tasks.router)
router.include_router(trees.router)
router.include_router(health.router)
