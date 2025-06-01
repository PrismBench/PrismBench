from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.v1.router import router as v1_router

# Define API metadata and tags
tags_metadata = [
    {
        "name": "Session",
        "description": "Operations for managing search sessions",
    },
    {
        "name": "Interaction",
        "description": "Endpoints for interacting with the search sessions",
    },
    {
        "name": "Tree",
        "description": "Tree structure operations",
    },
    {
        "name": "Health",
        "description": "Health check endpoints",
    },
]


def create_app() -> FastAPI:
    """
    Application factory for creating the FastAPI app.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Initialize FastAPI app
    app = FastAPI(
        title="PrismBench Search Interface",
        description="API for interacting with PrismBench's search algorithms",
        version="0.1.0",
        openapi_tags=tags_metadata,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    # Include the v1 router
    app.include_router(v1_router)

    # Add a root endpoint
    @app.get("/")
    async def root() -> Dict[str, Any]:
        """
        Root endpoint that provides basic API information.

        Returns:
            JSON with API information and links to documentation
        """
        return {
            "message": "PrismBench - Search Interface",
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
        }

    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting PrismBench Search Interface")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
