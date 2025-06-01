from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.v1.router import router as v1_router

# Define API metadata and tags
tags_metadata = [
    {
        "name": "Environment",
        "description": "Operations for running coding challenges",
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
        title="PrismBench Environment Service",
        description="API for running coding challenges in various environments",
        version="1.0.0",
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
    async def root() -> Dict[str, str]:
        """
        Root endpoint that provides basic API information.

        Returns:
            JSON with API information and links to documentation
        """
        return {
            "message": "PrismBench - Environment Service - Alive",
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }

    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting PrismBench Environment Service")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
