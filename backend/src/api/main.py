"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import content, metrics, config, auth, health
from src.core.scheduler import scheduler
from src.database.connection import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await db.connect()
    await db.initialize()
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()
    await db.disconnect()


app = FastAPI(
    title="AI News Influencer API",
    description="Autonomous AI Social Media Management System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(content.router, prefix="/api/v1", tags=["Content"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])
app.include_router(config.router, prefix="/api/v1", tags=["Configuration"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
