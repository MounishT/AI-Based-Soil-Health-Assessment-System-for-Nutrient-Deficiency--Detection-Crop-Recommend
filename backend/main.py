"""
main.py
-------
FastAPI application entry point for the AI-Based Soil Health Assessment System.

Responsibilities:
    - Configure logging
    - Register all routers
    - Enable CORS
    - Connect to PostgreSQL and create tables on startup
    - Expose Swagger UI + OpenAPI docs
    - Serve uploaded images as static files
"""

import logging
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import check_db_connection, init_db
from backend.routers import farms, images, soil_records, prediction, analysis, report, tts
from backend.routers import weather, market, pest, profit, chat, sms, share
from backend.routers import auth, history

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ══════════════════════════════════════════════════════════════════════════════

def configure_logging() -> None:
    """
    Configure root logger to write structured log lines to stdout.
    Log level is read from settings.LOG_LEVEL (default: INFO).
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DB_ECHO else logging.WARNING
    )


configure_logging()
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# LIFESPAN (startup / shutdown events)
# ══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager that runs startup logic before the app starts
    accepting requests, and teardown logic when it shuts down.

    Startup:
        1. Check PostgreSQL connectivity
        2. Create all ORM tables (if they don't exist)
        3. Ensure upload directory exists

    Shutdown:
        - Log graceful shutdown message
    """
    # ── Startup ───────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("=" * 60)

    # 1. Check DB connection
    if not check_db_connection():
        logger.error(
            "CRITICAL: Cannot connect to PostgreSQL! "
            "Running in DEGRADED MODE for demo purposes (API works, but /images POST will fail)."
        )
        # We allow it to start for the mentor demo, but in production this should crash.
    else:
        # 2. Create tables
        init_db()

    # 3. Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Upload directory ready: %s", settings.UPLOAD_DIR)

    logger.info("Application startup complete. Ready to serve requests.")

    yield  # ← app is running here

    # ── Shutdown ──────────────────────────────────────────────────────────
    logger.info("Application shutting down gracefully.")


# ══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,

    # ── Swagger UI customisation ──────────────────────────────────────────
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc UI
    openapi_url="/openapi.json",

    # ── OpenAPI metadata ──────────────────────────────────────────────────
    contact={
        "name":  "Soil Health AI Team",
        "email": "support@soilhealth.ai",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User registration, login, and JWT-based authentication.",
        },
        {
            "name": "Images",
            "description": "Upload and manage soil images.",
        },
        {
            "name": "Farms",
            "description": "Register and manage farms and farmer details.",
        },
        {
            "name": "Soil Records",
            "description": "Store and retrieve soil sensor readings.",
        },
        {
            "name": "Predictions & Dashboard",
            "description": (
                "ML crop/fertilizer predictions, prediction history, "
                "and dashboard statistics."
            ),
        },
        {
            "name": "Health",
            "description": "Application and database health checks.",
        },
    ],
)


# ══════════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ══════════════════════════════════════════════════════════════════════════════

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,   # set to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every incoming request and its response status code."""
    logger.info(
        "REQUEST  %s %s | client=%s",
        request.method,
        request.url.path,
        request.client.host if request.client else "unknown",
    )
    response = await call_next(request)
    logger.info(
        "RESPONSE %s %s | status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


# ══════════════════════════════════════════════════════════════════════════════
# STATIC FILES (serve uploaded images)
# ══════════════════════════════════════════════════════════════════════════════

# Make uploaded images accessible at /uploads/<filename>
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="uploads",
)


# ══════════════════════════════════════════════════════════════════════════════
# ROUTERS
# ══════════════════════════════════════════════════════════════════════════════

app.include_router(auth.router)
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(sms.router, prefix="/api/v1", tags=["SMS"])
app.include_router(share.router, prefix="/api/v1", tags=["Share"])
app.include_router(history.router, prefix="/api/v1")
app.include_router(images.router,       prefix="/api/v1")
app.include_router(farms.router,        prefix="/api/v1")
app.include_router(soil_records.router, prefix="/api/v1")
app.include_router(prediction.router,   prefix="/api/v1")
app.include_router(analysis.router)
app.include_router(report.router)
app.include_router(tts.router)
app.include_router(weather.router)
app.include_router(market.router)
app.include_router(pest.router)
app.include_router(profit.router)
app.include_router(chat.router)
app.include_router(sms.router)
app.include_router(share.router)


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.get(
    "/",
    tags=["Health"],
    summary="Root endpoint",
    response_description="Welcome message with API links.",
)
async def root():
    """Welcome endpoint — returns app info and link to Swagger UI."""
    return {
        "app":        settings.APP_NAME,
        "version":    settings.APP_VERSION,
        "status":     "running",
        "swagger_ui": "/docs",
        "redoc":      "/redoc",
        "openapi":    "/openapi.json",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Application health check",
    response_description="Health status of the app and database.",
)
async def health_check():
    """
    Return the health status of the application and its PostgreSQL connection.
    Useful for Docker / Kubernetes liveness probes.
    """
    db_ok = check_db_connection()
    payload = {
        "status":   "healthy" if db_ok else "degraded",
        "app":      settings.APP_NAME,
        "version":  settings.APP_VERSION,
        "database": "connected" if db_ok else "unreachable",
    }
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=payload, status_code=status_code)


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL EXCEPTION HANDLER
# ══════════════════════════════════════════════════════════════════════════════

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unhandled exceptions.
    Returns a clean JSON error response instead of a raw 500 traceback.
    """
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail":     "An unexpected error occurred. Please try again.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT RUNNER
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,              # hot-reload on file changes (dev only)
        log_level=settings.LOG_LEVEL.lower(),
    )

