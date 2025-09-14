"""
API response models
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool = Field(default=True)
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    documentation_url: str = Field(default="https://docs.voltagegpu.com/api/errors")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: int
    services: Dict[str, str] = Field(default_factory=dict)


class RateLimitInfo(BaseModel):
    """Rate limit information"""
    limit: int
    remaining: int
    reset_at: datetime
    retry_after: Optional[int] = None


class WebhookEvent(BaseModel):
    """Webhook event model"""
    id: str
    type: str
    created_at: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationMessage(BaseModel):
    """Notification message"""
    id: str
    user_id: str
    type: str = Field(..., description="info, warning, error, success")
    title: str
    message: str
    created_at: datetime
    read: bool = Field(default=False)
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskStatus(BaseModel):
    """Async task status"""
    task_id: str
    status: str = Field(..., description="pending, running, completed, failed")
    progress: int = Field(default=0, ge=0, le=100)
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None


class ValidationError(BaseModel):
    """Validation error detail"""
    field: str
    message: str
    type: str
    context: Optional[Dict[str, Any]] = None


class BatchOperationResult(BaseModel):
    """Batch operation result"""
    total: int
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    duration_ms: int


class SystemMessage(BaseModel):
    """System-wide message/announcement"""
    id: str
    title: str
    message: str
    severity: str = Field(..., description="info, warning, critical")
    active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    affected_services: List[str] = Field(default_factory=list)
