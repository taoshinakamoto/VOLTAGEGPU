"""
AI generation endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Dict, Any
from loguru import logger

from app.models.response import APIResponse
from app.services.proxy import ProxyService
from app.services.pricing import PricingService
from app.api.deps import get_api_key

router = APIRouter()
proxy_service = ProxyService()
pricing_service = PricingService()


@router.post("/generate/image", response_model=APIResponse[dict])
async def generate_image(
    prompt: str,
    model: str = "stable-diffusion-xl",
    width: int = Query(1024, ge=256, le=2048),
    height: int = Query(1024, ge=256, le=2048),
    steps: int = Query(50, ge=1, le=150),
    guidance_scale: float = Query(7.5, ge=1.0, le=20.0),
    negative_prompt: Optional[str] = None,
    seed: Optional[int] = None,
    api_key: str = Depends(get_api_key)
):
    """Generate an image using AI models"""
    try:
        generation_params = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale": guidance_scale,
            "negative_prompt": negative_prompt,
            "seed": seed
        }
        
        logger.info(f"Generating image with params: {generation_params}")
        
        # Forward request to backend
        backend_response = await proxy_service.generate_image(generation_params)
        
        # Apply pricing markup to any cost fields
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Image generation started successfully"
        )
    except Exception as e:
        logger.error(f"Failed to generate image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/video", response_model=APIResponse[dict])
async def generate_video(
    prompt: str,
    model: str = "stable-video-diffusion",
    duration_seconds: int = Query(4, ge=1, le=10),
    fps: int = Query(24, ge=8, le=60),
    width: int = Query(1024, ge=256, le=1920),
    height: int = Query(576, ge=256, le=1080),
    api_key: str = Depends(get_api_key)
):
    """Generate a video using AI models"""
    try:
        generation_params = {
            "prompt": prompt,
            "model": model,
            "duration_seconds": duration_seconds,
            "fps": fps,
            "width": width,
            "height": height
        }
        
        logger.info(f"Generating video with params: {generation_params}")
        
        # Mock response for now - would forward to backend
        response = {
            "job_id": "video_gen_001",
            "status": "processing",
            "estimated_time_seconds": 120,
            "cost_estimate": pricing_service.apply_markup(5.0)
        }
        
        return APIResponse(
            success=True,
            data=response,
            message="Video generation started successfully"
        )
    except Exception as e:
        logger.error(f"Failed to generate video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/inference", response_model=APIResponse[dict])
async def run_inference(
    model_id: str,
    input_data: Dict[str, Any],
    api_key: str = Depends(get_api_key)
):
    """Run inference on a custom model"""
    try:
        inference_params = {
            "model_id": model_id,
            "input_data": input_data
        }
        
        logger.info(f"Running inference with model: {model_id}")
        
        # Forward request to backend
        backend_response = await proxy_service.run_model_inference(inference_params)
        
        # Apply pricing markup
        response_with_markup = pricing_service.apply_markup_to_response(backend_response)
        
        return APIResponse(
            success=True,
            data=response_with_markup,
            message="Inference completed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to run inference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=APIResponse[list])
async def list_available_models(
    category: Optional[str] = Query(None, description="Model category: image, video, text, audio"),
    api_key: str = Depends(get_api_key)
):
    """List available AI models"""
    try:
        # Mock model list - in production, this would come from backend
        models = [
            {
                "id": "stable-diffusion-xl",
                "name": "Stable Diffusion XL",
                "category": "image",
                "description": "High-quality image generation",
                "cost_per_generation": pricing_service.apply_markup(0.05)
            },
            {
                "id": "stable-video-diffusion",
                "name": "Stable Video Diffusion",
                "category": "video",
                "description": "AI video generation",
                "cost_per_second": pricing_service.apply_markup(1.0)
            },
            {
                "id": "llama-2-70b",
                "name": "Llama 2 70B",
                "category": "text",
                "description": "Large language model",
                "cost_per_1k_tokens": pricing_service.apply_markup(0.01)
            }
        ]
        
        if category:
            models = [m for m in models if m["category"] == category]
        
        return APIResponse(
            success=True,
            data=models,
            message="Models retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generation/{job_id}", response_model=APIResponse[dict])
async def get_generation_status(
    job_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get status of an AI generation job"""
    try:
        # Mock status - in production, this would query backend
        status = {
            "job_id": job_id,
            "status": "completed",
            "progress": 100,
            "result_url": f"https://storage.voltagegpu.com/results/{job_id}/output.png",
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:02:00Z",
            "cost": pricing_service.apply_markup(0.05)
        }
        
        return APIResponse(
            success=True,
            data=status,
            message="Generation status retrieved"
        )
    except Exception as e:
        logger.error(f"Failed to get generation status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
