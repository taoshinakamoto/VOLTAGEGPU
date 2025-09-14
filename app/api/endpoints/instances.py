"""
Compute instances endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from loguru import logger

from app.models.instance import (
    InstanceCreateRequest,
    InstanceInfo,
    InstanceUpdateRequest,
    InstanceActionRequest,
    InstanceListResponse,
    InstanceMetrics,
    InstanceConsoleOutput
)
from app.models.response import APIResponse
from app.services.proxy import ProxyService
from app.services.pricing import PricingService
from app.api.deps import get_current_user, get_api_key

router = APIRouter()
proxy_service = ProxyService()
pricing_service = PricingService()


@router.post("/", response_model=APIResponse[InstanceInfo])
async def create_instance(
    request: InstanceCreateRequest,
    api_key: str = Depends(get_api_key)
):
    """Create a new GPU compute instance"""
    try:
        logger.info(f"Creating instance: {request.dict()}")
        
        # Forward request to backend
        backend_response = await proxy_service.create_instance(request.dict())
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Instance created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create instance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=APIResponse[InstanceListResponse])
async def list_instances(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    gpu_type: Optional[str] = None,
    region: Optional[str] = None,
    api_key: str = Depends(get_api_key)
):
    """List all compute instances"""
    try:
        filters = {
            "page": page,
            "per_page": per_page
        }
        if status:
            filters["status"] = status
        if gpu_type:
            filters["gpu_type"] = gpu_type
        if region:
            filters["region"] = region
        
        # Forward request to backend
        backend_response = await proxy_service.list_instances(filters)
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Instances retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list instances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}", response_model=APIResponse[InstanceInfo])
async def get_instance(
    instance_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get instance details"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.get_instance(instance_id)
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Instance retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{instance_id}", response_model=APIResponse[InstanceInfo])
async def update_instance(
    instance_id: str,
    request: InstanceUpdateRequest,
    api_key: str = Depends(get_api_key)
):
    """Update instance configuration"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.update_instance(instance_id, request.dict(exclude_unset=True))
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Instance updated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to update instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{instance_id}", response_model=APIResponse[dict])
async def terminate_instance(
    instance_id: str,
    api_key: str = Depends(get_api_key)
):
    """Terminate an instance"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.delete_instance(instance_id)
        
        return APIResponse(
            success=True,
            data=backend_response,
            message="Instance terminated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to terminate instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{instance_id}/actions", response_model=APIResponse[dict])
async def instance_action(
    instance_id: str,
    request: InstanceActionRequest,
    api_key: str = Depends(get_api_key)
):
    """Perform an action on an instance (start, stop, restart)"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.instance_action(instance_id, request.action)
        
        return APIResponse(
            success=True,
            data=backend_response,
            message=f"Action '{request.action}' executed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to perform action on instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}/metrics", response_model=APIResponse[InstanceMetrics])
async def get_instance_metrics(
    instance_id: str,
    period: str = Query("1h", regex="^(1h|6h|12h|24h|7d|30d)$"),
    api_key: str = Depends(get_api_key)
):
    """Get instance performance metrics"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.get_instance_metrics(instance_id, period)
        
        return APIResponse(
            success=True,
            data=backend_response,
            message="Metrics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get metrics for instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{instance_id}/logs", response_model=APIResponse[InstanceConsoleOutput])
async def get_instance_logs(
    instance_id: str,
    lines: int = Query(100, ge=1, le=10000),
    api_key: str = Depends(get_api_key)
):
    """Get instance console logs"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.get_instance_logs(instance_id, lines)
        
        return APIResponse(
            success=True,
            data=backend_response,
            message="Logs retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get logs for instance {instance_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
