"""
User management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from loguru import logger

from app.models.user import (
    UserInfo,
    UserUpdateRequest,
    UserUsageStats,
    BillingInfo,
    APIKey
)
from app.models.response import APIResponse
from app.services.auth import AuthService
from app.api.deps import get_current_user, require_admin

router = APIRouter()
auth_service = AuthService()


@router.get("/me", response_model=APIResponse[UserInfo])
async def get_current_user_info(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get current user information"""
    try:
        return APIResponse(
            success=True,
            data=current_user,
            message="User information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get user info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/me", response_model=APIResponse[UserInfo])
async def update_current_user(
    request: UserUpdateRequest,
    current_user: UserInfo = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Update user fields
        if request.full_name:
            current_user.full_name = request.full_name
        if request.company:
            current_user.company = request.company
        if request.phone:
            current_user.phone = request.phone
        if request.country:
            current_user.country = request.country
        if request.two_factor_enabled is not None:
            current_user.two_factor_enabled = request.two_factor_enabled
        
        # In production, this would update the database
        logger.info(f"Updated user profile for {current_user.id}")
        
        return APIResponse(
            success=True,
            data=current_user,
            message="Profile updated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/usage", response_model=APIResponse[UserUsageStats])
async def get_user_usage_stats(
    period: str = Query("monthly", regex="^(daily|weekly|monthly)$"),
    current_user: UserInfo = Depends(get_current_user)
):
    """Get current user's usage statistics"""
    try:
        # Mock usage stats - in production, this would aggregate from database
        stats = UserUsageStats(
            user_id=current_user.id,
            period=period,
            gpu_hours=150.5,
            instances_created=25,
            total_cost=1505.0,
            credits_used=150500,
            api_calls=5000,
            data_transferred_gb=250.5,
            average_instance_duration_hours=6.02,
            most_used_gpu="RTX_4090",
            most_used_region="us-east-1"
        )
        
        return APIResponse(
            success=True,
            data=stats,
            message="Usage statistics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get usage stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/billing", response_model=APIResponse[BillingInfo])
async def get_billing_info(
    current_user: UserInfo = Depends(get_current_user)
):
    """Get current user's billing information"""
    try:
        # Mock billing info - in production, this would query database
        billing = BillingInfo(
            user_id=current_user.id,
            payment_method="Credit Card ending in 4242",
            billing_address={
                "line1": "123 Tech Street",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105",
                "country": "US"
            },
            currency="USD",
            auto_recharge=True,
            auto_recharge_amount=100.0,
            auto_recharge_threshold=10.0,
            invoices=[
                {
                    "invoice_id": "inv_001",
                    "date": "2024-01-01",
                    "amount": 100.0,
                    "status": "paid"
                }
            ]
        )
        
        return APIResponse(
            success=True,
            data=billing,
            message="Billing information retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get billing info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me/api-keys", response_model=APIResponse[List[APIKey]])
async def list_api_keys(
    current_user: UserInfo = Depends(get_current_user)
):
    """List current user's API keys"""
    try:
        # Mock API keys - in production, this would query database
        api_keys = [
            APIKey(
                id="key_001",
                name="Production Key",
                key_preview="vgpu_AbCd",
                created_at="2024-01-01T00:00:00Z",
                last_used="2024-01-15T00:00:00Z",
                permissions=["read", "write"],
                is_active=True
            ),
            APIKey(
                id="key_002",
                name="Development Key",
                key_preview="vgpu_EfGh",
                created_at="2024-01-05T00:00:00Z",
                permissions=["read"],
                is_active=True
            )
        ]
        
        return APIResponse(
            success=True,
            data=api_keys,
            message="API keys retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list API keys: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me/api-keys/{key_id}", response_model=APIResponse[dict])
async def delete_api_key(
    key_id: str,
    current_user: UserInfo = Depends(get_current_user)
):
    """Delete an API key"""
    try:
        # In production, this would delete from database
        logger.info(f"Deleting API key {key_id} for user {current_user.id}")
        
        return APIResponse(
            success=True,
            data={"message": "API key deleted successfully"},
            message="API key deleted"
        )
    except Exception as e:
        logger.error(f"Failed to delete API key: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Admin endpoints
@router.get("/", response_model=APIResponse[List[UserInfo]])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    tier: Optional[str] = None,
    current_user: UserInfo = Depends(require_admin)
):
    """List all users (admin only)"""
    try:
        # Mock user list - in production, this would query database
        users = [
            UserInfo(
                id="user_001",
                email="user1@example.com",
                full_name="User One",
                role="user",
                status="active",
                tier="professional",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                email_verified=True,
                credit_balance=500.0
            ),
            UserInfo(
                id="user_002",
                email="user2@example.com",
                full_name="User Two",
                role="user",
                status="active",
                tier="starter",
                created_at="2024-01-02T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
                email_verified=True,
                credit_balance=100.0
            )
        ]
        
        if status:
            users = [u for u in users if u.status == status]
        if tier:
            users = [u for u in users if u.tier == tier]
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_users = users[start:end]
        
        return APIResponse(
            success=True,
            data=paginated_users,
            message="Users retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to list users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=APIResponse[UserInfo])
async def get_user_by_id(
    user_id: str,
    current_user: UserInfo = Depends(require_admin)
):
    """Get user by ID (admin only)"""
    try:
        # Mock user - in production, this would query database
        user = UserInfo(
            id=user_id,
            email="user@example.com",
            full_name="Example User",
            role="user",
            status="active",
            tier="professional",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            email_verified=True,
            credit_balance=1000.0
        )
        
        return APIResponse(
            success=True,
            data=user,
            message="User retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/status", response_model=APIResponse[UserInfo])
async def update_user_status(
    user_id: str,
    status: str,
    current_user: UserInfo = Depends(require_admin)
):
    """Update user status (admin only)"""
    try:
        # In production, this would update database
        logger.info(f"Admin {current_user.id} updating status for user {user_id} to {status}")
        
        # Mock updated user
        user = UserInfo(
            id=user_id,
            email="user@example.com",
            full_name="Example User",
            role="user",
            status=status,
            tier="professional",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            email_verified=True,
            credit_balance=1000.0
        )
        
        return APIResponse(
            success=True,
            data=user,
            message=f"User status updated to {status}"
        )
    except Exception as e:
        logger.error(f"Failed to update user status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/credits", response_model=APIResponse[dict])
async def add_credits_to_user(
    user_id: str,
    amount: float = Query(..., gt=0),
    reason: str = None,
    current_user: UserInfo = Depends(require_admin)
):
    """Add credits to user account (admin only)"""
    try:
        # In production, this would update database
        logger.info(f"Admin {current_user.id} adding {amount} credits to user {user_id}")
        
        return APIResponse(
            success=True,
            data={
                "user_id": user_id,
                "credits_added": amount,
                "new_balance": 1000.0 + amount,
                "reason": reason
            },
            message=f"Successfully added {amount} credits"
        )
    except Exception as e:
        logger.error(f"Failed to add credits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
