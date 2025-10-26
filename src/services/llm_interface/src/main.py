from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .api.v1.router import router as api_router

# Define API metadata and tags
tags_metadata = [
    {
        "name": "Session",
        "description": "Operations for managing LLM sessions",
    },
    {
        "name": "Interaction",
        "description": "Endpoints for interacting with LLM models",
    },
    {
        "name": "History",
        "description": "Operations related to conversation history",
    },
    {
        "name": "Health",
        "description": "Health check endpoints",
    },
]

# Initialize FastAPI app
app = FastAPI(
    title="PrismBench LLM Interface",
    description="API for interacting with LLMs through a unified interface",
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

# Include the versioned API router
app.include_router(api_router)


# Add a root endpoint
@app.get(
    "/",
)
async def root() -> Dict[str, str]:
    """
    Root endpoint that provides basic API information.

    Returns:
        JSON with API information and links to documentation
    """
    return {
        "message": "PrismBench - LLM Interface - Alive",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting PrismBench LLM Interface")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
