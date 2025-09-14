"""
Batch job endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from loguru import logger
from datetime import datetime

from app.models.response import APIResponse, TaskStatus
from app.services.proxy import ProxyService
from app.services.pricing import PricingService
from app.api.deps import get_api_key

router = APIRouter()
proxy_service = ProxyService()
pricing_service = PricingService()


@router.post("/jobs", response_model=APIResponse[dict])
async def submit_batch_job(
    job_name: str,
    gpu_type: str,
    gpu_count: int = Query(1, ge=1, le=8),
    container_image: str = "pytorch:latest",
    command: str = None,
    input_data_url: Optional[str] = None,
    output_location: Optional[str] = None,
    environment_variables: Optional[Dict[str, str]] = None,
    timeout_hours: float = Query(24, gt=0, le=168),  # Max 1 week
    api_key: str = Depends(get_api_key)
):
    """Submit a batch processing job"""
    try:
        job_data = {
            "job_name": job_name,
            "gpu_type": gpu_type,
            "gpu_count": gpu_count,
            "container_image": container_image,
            "command": command,
            "input_data_url": input_data_url,
            "output_location": output_location,
            "environment_variables": environment_variables or {},
            "timeout_hours": timeout_hours
        }
        
        logger.info(f"Submitting batch job: {job_name}")
        
        # Forward request to backend
        backend_response = await proxy_service.submit_batch_job(job_data)
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Batch job submitted successfully"
        )
    except Exception as e:
        logger.error(f"Failed to submit batch job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs", response_model=APIResponse[List[dict]])
async def list_batch_jobs(
    status: Optional[str] = Query(None, description="Filter by status: pending, running, completed, failed"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    api_key: str = Depends(get_api_key)
):
    """List all batch jobs"""
    try:
        # Mock batch jobs - in production, this would query backend
        jobs = [
            {
                "job_id": "batch_001",
                "job_name": "Training Job",
                "status": "running",
                "progress": 45,
                "gpu_type": "A100",
                "gpu_count": 4,
                "started_at": datetime.utcnow().isoformat(),
                "estimated_cost": pricing_service.apply_markup(150.0),
                "current_cost": pricing_service.apply_markup(67.5)
            },
            {
                "job_id": "batch_002",
                "job_name": "Inference Batch",
                "status": "completed",
                "progress": 100,
                "gpu_type": "RTX_4090",
                "gpu_count": 2,
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "total_cost": pricing_service.apply_markup(25.0)
            }
        ]
        
        if status:
            jobs = [j for j in jobs if j["status"] == status]
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_jobs = jobs[start:end]
        
        return APIResponse(
            success=True,
            data=paginated_jobs,
            message="Batch jobs retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list batch jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=APIResponse[dict])
async def get_batch_job(
    job_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get batch job details"""
    try:
        # Forward request to backend
        backend_response = await proxy_service.get_batch_job_status(job_id)
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Batch job details retrieved"
        )
    except Exception as e:
        logger.error(f"Failed to get batch job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/cancel", response_model=APIResponse[dict])
async def cancel_batch_job(
    job_id: str,
    api_key: str = Depends(get_api_key)
):
    """Cancel a running batch job"""
    try:
        # Mock cancellation - in production, this would call backend
        logger.info(f"Cancelling batch job: {job_id}")
        
        response = {
            "job_id": job_id,
            "status": "cancelled",
            "message": "Job cancelled successfully",
            "refund_amount": pricing_service.apply_markup(10.0)
        }
        
        return APIResponse(
            success=True,
            data=response,
            message="Batch job cancelled"
        )
    except Exception as e:
        logger.error(f"Failed to cancel batch job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}/logs", response_model=APIResponse[dict])
async def get_batch_job_logs(
    job_id: str,
    lines: int = Query(100, ge=1, le=10000),
    api_key: str = Depends(get_api_key)
):
    """Get batch job logs"""
    try:
        # Mock logs - in production, this would fetch from backend
        logs = {
            "job_id": job_id,
            "logs": [
                "2024-01-01 00:00:00 - Job started",
                "2024-01-01 00:00:01 - Loading model...",
                "2024-01-01 00:00:10 - Model loaded successfully",
                "2024-01-01 00:00:11 - Processing batch 1/100...",
            ],
            "has_more": True,
            "total_lines": 1523
        }
        
        return APIResponse(
            success=True,
            data=logs,
            message="Logs retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get logs for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}/results", response_model=APIResponse[dict])
async def get_batch_job_results(
    job_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get batch job results"""
    try:
        # Mock results - in production, this would fetch from backend
        results = {
            "job_id": job_id,
            "status": "completed",
            "output_location": f"s3://voltagegpu-results/{job_id}/",
            "files": [
                {
                    "name": "output.json",
                    "size_bytes": 1024567,
                    "url": f"https://storage.voltagegpu.com/jobs/{job_id}/output.json"
                },
                {
                    "name": "metrics.csv",
                    "size_bytes": 45678,
                    "url": f"https://storage.voltagegpu.com/jobs/{job_id}/metrics.csv"
                }
            ],
            "total_cost": pricing_service.apply_markup(25.0),
            "runtime_hours": 2.5
        }
        
        return APIResponse(
            success=True,
            data=results,
            message="Job results retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get results for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates", response_model=APIResponse[dict])
async def create_job_template(
    template_name: str,
    description: str,
    gpu_type: str,
    gpu_count: int,
    container_image: str,
    default_command: Optional[str] = None,
    default_environment: Optional[Dict[str, str]] = None,
    api_key: str = Depends(get_api_key)
):
    """Create a reusable job template"""
    try:
        template = {
            "template_id": f"tmpl_{template_name.lower().replace(' ', '_')}",
            "template_name": template_name,
            "description": description,
            "gpu_type": gpu_type,
            "gpu_count": gpu_count,
            "container_image": container_image,
            "default_command": default_command,
            "default_environment": default_environment or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Creating job template: {template_name}")
        
        return APIResponse(
            success=True,
            data=template,
            message="Job template created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create job template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
