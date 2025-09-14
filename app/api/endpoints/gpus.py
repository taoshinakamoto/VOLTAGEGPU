"""
GPU resources endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from loguru import logger

from app.models.gpu import (
    GPUInfo,
    GPUListResponse,
    GPUAvailability,
    GPUMetrics,
    GPUType,
    Region
)
from app.models.response import APIResponse
from app.services.proxy import ProxyService
from app.services.pricing import PricingService
from app.api.deps import get_optional_api_key

router = APIRouter()
proxy_service = ProxyService()
pricing_service = PricingService()


@router.get("/available", response_model=APIResponse[List[GPUInfo]])
async def list_available_gpus(
    gpu_type: Optional[GPUType] = None,
    region: Optional[Region] = None,
    min_vram: Optional[int] = Query(None, ge=1),
    max_price: Optional[float] = Query(None, gt=0),
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """List all available GPUs with current pricing"""
    try:
        filters = {}
        if gpu_type:
            filters["gpu_type"] = gpu_type
        if region:
            filters["region"] = region
        if min_vram:
            filters["min_vram"] = min_vram
        if max_price:
            # Adjust max_price for backend (remove markup)
            filters["max_price"] = max_price / pricing_service.markup
        
        # Forward request to backend
        backend_response = await proxy_service.get_gpu_availability(filters)
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Available GPUs retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list available GPUs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", response_model=APIResponse[List[str]])
async def list_gpu_types():
    """List all supported GPU types"""
    try:
        gpu_types = [gpu.value for gpu in GPUType]
        
        return APIResponse(
            success=True,
            data=gpu_types,
            message="GPU types retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list GPU types: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions", response_model=APIResponse[List[str]])
async def list_regions():
    """List all available regions"""
    try:
        regions = [region.value for region in Region]
        
        return APIResponse(
            success=True,
            data=regions,
            message="Regions retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list regions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/availability/{gpu_type}", response_model=APIResponse[GPUAvailability])
async def check_gpu_availability(
    gpu_type: GPUType,
    region: Optional[Region] = None,
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """Check availability of a specific GPU type"""
    try:
        filters = {"gpu_type": gpu_type}
        if region:
            filters["region"] = region
        
        # Forward request to backend
        backend_response = await proxy_service.get_gpu_availability(filters)
        
        # Process availability data
        if backend_response and len(backend_response) > 0:
            gpu_data = backend_response[0]
            availability = GPUAvailability(
                gpu_type=gpu_type,
                region=region or Region.US_EAST_1,
                available=gpu_data.get("available_count", 0),
                total=gpu_data.get("total_count", 0),
                spot_available=gpu_data.get("spot_available", False),
                spot_price=pricing_service.apply_markup(gpu_data.get("spot_price", 0)) if gpu_data.get("spot_price") else None
            )
        else:
            availability = GPUAvailability(
                gpu_type=gpu_type,
                region=region or Region.US_EAST_1,
                available=0,
                total=0,
                spot_available=False
            )
        
        return APIResponse(
            success=True,
            data=availability,
            message="GPU availability checked successfully"
        )
    except Exception as e:
        logger.error(f"Failed to check GPU availability: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/specs/{gpu_type}", response_model=APIResponse[dict])
async def get_gpu_specs(
    gpu_type: GPUType,
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """Get detailed specifications for a GPU type"""
    try:
        # Hardcoded specs for now - in production, this would come from database
        specs = {
            GPUType.RTX_4090: {
                "name": "NVIDIA RTX 4090",
                "vram": 24,
                "memory_bandwidth": 1008,
                "fp32_tflops": 82.6,
                "fp16_tflops": 165.2,
                "cuda_cores": 16384,
                "tensor_cores": 512,
                "architecture": "Ada Lovelace",
                "tdp": 450
            },
            GPUType.A100: {
                "name": "NVIDIA A100",
                "vram": 80,
                "memory_bandwidth": 2039,
                "fp32_tflops": 19.5,
                "fp16_tflops": 312,
                "cuda_cores": 6912,
                "tensor_cores": 432,
                "architecture": "Ampere",
                "tdp": 400
            },
            GPUType.H100: {
                "name": "NVIDIA H100",
                "vram": 80,
                "memory_bandwidth": 3352,
                "fp32_tflops": 60,
                "fp16_tflops": 989,
                "cuda_cores": 14592,
                "tensor_cores": 456,
                "architecture": "Hopper",
                "tdp": 700
            }
        }
        
        gpu_spec = specs.get(gpu_type, {
            "name": gpu_type.value,
            "vram": 16,
            "memory_bandwidth": 500,
            "fp32_tflops": 20,
            "fp16_tflops": 40,
            "architecture": "Unknown",
            "tdp": 300
        })
        
        return APIResponse(
            success=True,
            data=gpu_spec,
            message="GPU specifications retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get GPU specs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
