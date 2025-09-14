"""
Pricing-related data models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from .gpu import GPUType, Region


class PricingTier(str, Enum):
    """Pricing tiers"""
    ON_DEMAND = "on_demand"
    SPOT = "spot"
    RESERVED = "reserved"
    COMMITMENT = "commitment"


class Currency(str, Enum):
    """Supported currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"


class BillingPeriod(str, Enum):
    """Billing periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class GPUPricing(BaseModel):
    """GPU pricing information"""
    gpu_type: GPUType
    region: Region
    tier: PricingTier
    price_per_hour: float
    price_per_minute: float
    spot_price: Optional[float] = None
    reserved_price_monthly: Optional[float] = None
    reserved_price_yearly: Optional[float] = None
    currency: Currency = Field(default=Currency.USD)
    minimum_commitment_hours: Optional[int] = None
    discount_percentage: float = Field(default=0.0, ge=0, le=100)
    effective_date: datetime
    expires_at: Optional[datetime] = None


class PriceEstimate(BaseModel):
    """Price estimate for a workload"""
    gpu_type: GPUType
    gpu_count: int
    region: Region
    duration_hours: float
    tier: PricingTier
    base_cost: float
    discount_amount: float = Field(default=0.0)
    tax_amount: float = Field(default=0.0)
    total_cost: float
    currency: Currency = Field(default=Currency.USD)
    breakdown: Dict[str, float] = Field(default_factory=dict)
    savings_compared_to_on_demand: Optional[float] = None


class Invoice(BaseModel):
    """Invoice model"""
    id: str
    user_id: str
    invoice_number: str
    status: str = Field(..., description="draft, pending, paid, overdue, cancelled")
    period_start: datetime
    period_end: datetime
    due_date: datetime
    subtotal: float
    tax_amount: float
    discount_amount: float
    total: float
    currency: Currency = Field(default=Currency.USD)
    payment_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    line_items: List[Dict[str, Any]]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreditTransaction(BaseModel):
    """Credit transaction"""
    id: str
    user_id: str
    type: str = Field(..., description="purchase, usage, refund, bonus")
    amount: float
    balance_before: float
    balance_after: float
    description: str
    reference_id: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UsageReport(BaseModel):
    """Usage report"""
    user_id: str
    period_start: datetime
    period_end: datetime
    total_gpu_hours: float
    total_cost: float
    instances_created: int
    average_gpu_count: float
    gpu_breakdown: Dict[GPUType, float]
    region_breakdown: Dict[Region, float]
    daily_usage: List[Dict[str, Any]]
    top_instances: List[Dict[str, Any]]
    cost_by_project: Dict[str, float]


class Discount(BaseModel):
    """Discount model"""
    id: str
    code: str
    description: str
    type: str = Field(..., description="percentage, fixed, credits")
    value: float
    minimum_spend: Optional[float] = None
    maximum_discount: Optional[float] = None
    valid_from: datetime
    valid_until: datetime
    usage_limit: Optional[int] = None
    usage_count: int = Field(default=0)
    applicable_gpus: List[GPUType] = Field(default_factory=list)
    applicable_regions: List[Region] = Field(default_factory=list)
    is_active: bool = Field(default=True)


class CommitmentPlan(BaseModel):
    """Commitment plan for discounted pricing"""
    id: str
    user_id: str
    name: str
    gpu_type: GPUType
    gpu_count: int
    region: Region
    commitment_hours: int
    hourly_rate: float
    total_value: float
    discount_percentage: float
    start_date: datetime
    end_date: datetime
    hours_used: float
    hours_remaining: float
    status: str = Field(..., description="active, expired, cancelled")
    auto_renew: bool = Field(default=False)


class CostOptimizationRecommendation(BaseModel):
    """Cost optimization recommendation"""
    recommendation_type: str
    title: str
    description: str
    current_cost: float
    estimated_savings: float
    estimated_new_cost: float
    implementation_steps: List[str]
    affected_resources: List[str]
    priority: str = Field(..., description="low, medium, high")
    effort: str = Field(..., description="low, medium, high")
