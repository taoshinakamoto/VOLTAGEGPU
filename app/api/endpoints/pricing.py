"""
Pricing and billing endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from loguru import logger
from datetime import datetime, timedelta

from app.models.pricing import (
    GPUPricing,
    PriceEstimate,
    Invoice,
    UsageReport,
    CostOptimizationRecommendation
)
from app.models.gpu import GPUType, Region
from app.models.response import APIResponse
from app.services.proxy import ProxyService
from app.services.pricing import PricingService
from app.api.deps import get_current_user, get_optional_api_key
from app.models.user import UserInfo

router = APIRouter()
proxy_service = ProxyService()
pricing_service = PricingService()


@router.get("/current", response_model=APIResponse[List[GPUPricing]])
async def get_current_pricing(
    gpu_type: Optional[GPUType] = None,
    region: Optional[Region] = None,
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """Get current pricing for GPU resources"""
    try:
        # Get pricing from backend
        backend_pricing = await proxy_service.get_pricing_info(gpu_type, region)
        
        # Apply markup
        pricing_with_markup = pricing_service.apply_markup_to_response(backend_pricing)
        
        return APIResponse(
            success=True,
            data=pricing_with_markup,
            message="Pricing information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get pricing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate", response_model=APIResponse[PriceEstimate])
async def estimate_cost(
    gpu_type: GPUType,
    gpu_count: int = Query(1, ge=1, le=8),
    duration_hours: float = Query(..., gt=0),
    region: Region = Region.US_EAST_1,
    instance_type: str = "on_demand",
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """Estimate cost for GPU usage"""
    try:
        # Get base pricing from backend
        backend_pricing = await proxy_service.get_pricing_info(gpu_type, region)
        
        # Extract base price
        base_price = backend_pricing.get("price_per_hour", 1.0)
        
        # Calculate with markup
        cost_breakdown = pricing_service.calculate_instance_cost(
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            duration_hours=duration_hours,
            base_price_per_hour=base_price,
            instance_type=instance_type
        )
        
        # Create estimate response
        estimate = PriceEstimate(
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            region=region,
            duration_hours=duration_hours,
            tier=instance_type,
            base_cost=cost_breakdown["hourly_rate"] * duration_hours,
            discount_amount=cost_breakdown.get("savings", 0),
            tax_amount=0,  # Could calculate tax based on region
            total_cost=cost_breakdown["total_cost"],
            breakdown=cost_breakdown
        )
        
        return APIResponse(
            success=True,
            data=estimate,
            message="Cost estimate calculated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to estimate cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices", response_model=APIResponse[List[Invoice]])
async def list_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: UserInfo = Depends(get_current_user)
):
    """List user invoices"""
    try:
        # Mock invoices - in production, this would query database
        invoices = [
            Invoice(
                id=f"inv_{current_user.id}_001",
                user_id=current_user.id,
                invoice_number="INV-2024-001",
                status="paid",
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=7),
                subtotal=1000.0,
                tax_amount=100.0,
                discount_amount=50.0,
                total=1050.0,
                paid_at=datetime.utcnow() - timedelta(days=5),
                line_items=[
                    {
                        "description": "GPU Usage - RTX 4090",
                        "quantity": 100,
                        "unit_price": 10.0,
                        "total": 1000.0
                    }
                ]
            )
        ]
        
        return APIResponse(
            success=True,
            data=invoices,
            message="Invoices retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage", response_model=APIResponse[UsageReport])
async def get_usage_report(
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    current_user: UserInfo = Depends(get_current_user)
):
    """Get usage report for current user"""
    try:
        # Mock usage report - in production, this would aggregate from database
        report = UsageReport(
            user_id=current_user.id,
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            total_gpu_hours=250.5,
            total_cost=2505.0,
            instances_created=15,
            average_gpu_count=2.5,
            gpu_breakdown={
                GPUType.RTX_4090: 150.0,
                GPUType.A100: 100.5
            },
            region_breakdown={
                Region.US_EAST_1: 200.0,
                Region.EU_WEST_1: 50.5
            },
            daily_usage=[
                {
                    "date": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "hours": 8.5,
                    "cost": 85.0
                }
                for i in range(7)
            ],
            top_instances=[
                {
                    "instance_id": "inst_001",
                    "gpu_type": "RTX_4090",
                    "hours": 50.0,
                    "cost": 500.0
                }
            ],
            cost_by_project={
                "default": 1500.0,
                "ml_training": 1005.0
            }
        )
        
        return APIResponse(
            success=True,
            data=report,
            message="Usage report generated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to generate usage report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=APIResponse[List[CostOptimizationRecommendation]])
async def get_cost_recommendations(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get cost optimization recommendations"""
    try:
        # Mock recommendations - in production, this would analyze usage patterns
        recommendations = [
            CostOptimizationRecommendation(
                recommendation_type="reserved_instances",
                title="Switch to Reserved Instances",
                description="Based on your usage patterns, switching to reserved instances could save you money",
                current_cost=1000.0,
                estimated_savings=400.0,
                estimated_new_cost=600.0,
                implementation_steps=[
                    "Review your consistent GPU usage patterns",
                    "Select appropriate reservation terms",
                    "Purchase reserved capacity",
                    "Monitor savings"
                ],
                affected_resources=["RTX_4090", "A100"],
                priority="high",
                effort="low"
            ),
            CostOptimizationRecommendation(
                recommendation_type="spot_instances",
                title="Use Spot Instances for Non-Critical Workloads",
                description="Leverage spot instances for batch jobs and fault-tolerant workloads",
                current_cost=500.0,
                estimated_savings=150.0,
                estimated_new_cost=350.0,
                implementation_steps=[
                    "Identify interruptible workloads",
                    "Implement checkpointing",
                    "Configure spot instance requests",
                    "Set up automatic failover"
                ],
                affected_resources=["batch_jobs"],
                priority="medium",
                effort="medium"
            )
        ]
        
        return APIResponse(
            success=True,
            data=recommendations,
            message="Cost optimization recommendations generated"
        )
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credits/purchase", response_model=APIResponse[dict])
async def purchase_credits(
    amount_usd: float = Query(..., gt=0),
    current_user: UserInfo = Depends(get_current_user)
):
    """Purchase credits for account"""
    try:
        credits = pricing_service.calculate_credits_needed(amount_usd)
        
        # In production, this would process payment and update database
        logger.info(f"User {current_user.id} purchasing {credits} credits for ${amount_usd}")
        
        return APIResponse(
            success=True,
            data={
                "credits_purchased": credits,
                "amount_charged": amount_usd,
                "new_balance": current_user.credit_balance + credits
            },
            message=f"Successfully purchased {credits} credits"
        )
    except Exception as e:
        logger.error(f"Failed to purchase credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
