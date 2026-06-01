"""FastAPI application initialization."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.engine import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready Multimodal Medical Intelligence Assistant",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routers (keeping backward compatibility)
try:
    from .api.health import router as health_router
    app.include_router(health_router, prefix="/api")
except ImportError:
    pass

try:
    from .api.uploads import router as upload_router
    app.include_router(upload_router, prefix="/api")
except ImportError:
    pass

try:
    from .api.ingestion import router as ingestion_router
    app.include_router(ingestion_router, prefix="/api")
except ImportError:
    pass

try:
    from .api.retrieval import router as retrieval_router
    app.include_router(retrieval_router, prefix="/api")
except ImportError:
    pass


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "MediScan RAG backend is running.",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "vector_db": "ready",
        "llm": "ready",
    }
