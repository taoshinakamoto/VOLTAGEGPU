"""
API endpoints for VoltageGPU
"""

from fastapi import APIRouter
from app.api.endpoints import (
    instances,
    gpus,
    auth,
    pricing,
    ai_generation,
    batch_jobs,
    users
)

# Create main router
router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["User Management"])
router.include_router(gpus.router, prefix="/gpus", tags=["GPU Resources"])
router.include_router(instances.router, prefix="/compute/instances", tags=["Compute Instances"])
router.include_router(pricing.router, prefix="/pricing", tags=["Pricing & Billing"])
router.include_router(ai_generation.router, prefix="/ai", tags=["AI Generation"])
router.include_router(batch_jobs.router, prefix="/batch", tags=["Batch Jobs"])
