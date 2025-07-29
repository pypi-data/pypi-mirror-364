"""
ACOLYTE API Module
Basic FastAPI application for the ACOLYTE backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers from submodules
from acolyte.api.index import router as index_router
from acolyte.api.openai import router as openai_router
from acolyte.api.dream import router as dream_router
from acolyte.api.health import router as health_router
from acolyte.api.websockets.progress import router as ws_progress_router

# Core imports for lifespan
from acolyte.core.logging import logger
from acolyte.core.secure_config import get_settings
from acolyte.services.chat_service import ChatService
from acolyte.services.conversation_service import ConversationService

__all__ = ["app"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with shared services to prevent memory leaks."""
    # Startup
    logger.info("ACOLYTE API starting up")

    # Create shared services (Singleton pattern)
    config = get_settings()
    context_size = config.get("model.context_size", 32768)

    app.state.chat_service = ChatService(context_size=context_size)
    app.state.conversation_service = ConversationService()

    logger.info("Shared services initialized", context_size=context_size)

    yield

    # Shutdown - Clean up resources
    logger.info("ACOLYTE API shutting down")

    # Clean up ChatService using its cleanup method
    if hasattr(app.state, 'chat_service') and app.state.chat_service:
        await app.state.chat_service.cleanup()

    logger.info("ACOLYTE API shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="ACOLYTE API",
    description="Local AI Programming Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Solo localhost en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ACOLYTE API is running"}


# Include all routers
app.include_router(openai_router, prefix="/v1", tags=["OpenAI"])
app.include_router(index_router, prefix="/api/index", tags=["Indexing"])
app.include_router(dream_router, prefix="/api/dream", tags=["Dream"])
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(ws_progress_router, prefix="/api/ws", tags=["WebSocket"])
