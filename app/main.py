"""
VoltageGPU API Main Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from contextlib import asynccontextmanager
import time
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.api import router
from app.models.response import ErrorResponse, HealthCheckResponse

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Track application start time
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API URL: {settings.BASE_URL}")
    logger.info(f"Pricing markup: {(settings.PRICING_MARKUP - 1) * 100}%")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="High-Performance GPU Computing Infrastructure API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and track metrics"""
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Track metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(duration)
    
    # Add custom headers
    response.headers["X-Response-Time"] = f"{duration:.3f}"
    response.headers["X-API-Version"] = settings.APP_VERSION
    
    # Log response
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred",
            status_code=500,
            request_id=request.headers.get("X-Request-ID")
        ).dict()
    )


# Root endpoint
@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Health check endpoint"""
    uptime = int(time.time() - app_start_time)
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        uptime_seconds=uptime,
        services={
            "api": "operational",
            "proxy": "operational",
            "auth": "operational",
            "pricing": "operational"
        }
    )


# Metrics endpoint
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    if settings.PROMETHEUS_ENABLED:
        return generate_latest()
    return "Metrics disabled"


# Include API routers
app.include_router(router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        workers=settings.WORKERS if not settings.DEBUG else 1
    )
