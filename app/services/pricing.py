"""
Pricing service with markup calculation
"""

from typing import Dict, Any, Optional, List
from app.core.config import settings
from loguru import logger


class PricingService:
    """Service for handling pricing with markup"""
    
    def __init__(self):
        """Initialize the pricing service"""
        self.markup = settings.PRICING_MARKUP
        logger.info(f"Pricing service initialized with {(self.markup - 1) * 100}% markup")
    
    def apply_markup(self, price: float) -> float:
        """
        Apply markup to a price
        
        Args:
            price: Original price
            
        Returns:
            Price with markup applied
        """
        return round(price * self.markup, 4)
    
    def apply_markup_to_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply markup to all price fields in a response
        
        Args:
            response: Response data from backend
            
        Returns:
            Response with markup applied to prices
        """
        # Common price field names to look for
        price_fields = [
            'price', 'cost', 'rate', 'amount', 'fee',
            'price_per_hour', 'price_per_minute', 'hourly_rate',
            'cost_per_hour', 'total_cost', 'base_cost',
            'spot_price', 'reserved_price_monthly', 'reserved_price_yearly'
        ]
        
        def apply_markup_recursive(data: Any) -> Any:
            """Recursively apply markup to nested structures"""
            if isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    # Check if this is a price field
                    if any(price_key in key.lower() for price_key in price_fields):
                        if isinstance(value, (int, float)) and value > 0:
                            result[key] = self.apply_markup(value)
                            logger.debug(f"Applied markup to {key}: {value} -> {result[key]}")
                        else:
                            result[key] = value
                    else:
                        result[key] = apply_markup_recursive(value)
                return result
            elif isinstance(data, list):
                return [apply_markup_recursive(item) for item in data]
            else:
                return data
        
        return apply_markup_recursive(response)
    
    def calculate_instance_cost(
        self,
        gpu_type: str,
        gpu_count: int,
        duration_hours: float,
        base_price_per_hour: float,
        instance_type: str = "on_demand"
    ) -> Dict[str, float]:
        """
        Calculate the total cost for an instance with markup
        
        Args:
            gpu_type: Type of GPU
            gpu_count: Number of GPUs
            duration_hours: Duration in hours
            base_price_per_hour: Base price per hour from backend
            instance_type: Type of instance (on_demand, spot, reserved)
            
        Returns:
            Cost breakdown with markup applied
        """
        # Apply discount based on instance type
        discount = 0.0
        if instance_type == "spot":
            discount = 0.3  # 30% discount for spot instances
        elif instance_type == "reserved":
            discount = 0.5  # 50% discount for reserved instances
        
        # Calculate base cost
        base_hourly = base_price_per_hour * gpu_count
        discounted_hourly = base_hourly * (1 - discount)
        
        # Apply markup
        marked_up_hourly = self.apply_markup(discounted_hourly)
        
        # Calculate total
        total_cost = marked_up_hourly * duration_hours
        
        return {
            "base_hourly_rate": base_price_per_hour,
            "gpu_count": gpu_count,
            "discount_percentage": discount * 100,
            "hourly_rate": marked_up_hourly,
            "duration_hours": duration_hours,
            "total_cost": round(total_cost, 2),
            "savings": round((base_hourly - discounted_hourly) * duration_hours, 2) if discount > 0 else 0
        }
    
    def get_tiered_pricing(self, base_price: float) -> Dict[str, float]:
        """
        Get tiered pricing with markup for different commitment levels
        
        Args:
            base_price: Base price from backend
            
        Returns:
            Tiered pricing with markup
        """
        return {
            "on_demand": self.apply_markup(base_price),
            "spot": self.apply_markup(base_price * 0.7),  # 30% discount
            "reserved_monthly": self.apply_markup(base_price * 0.6),  # 40% discount
            "reserved_yearly": self.apply_markup(base_price * 0.5),  # 50% discount
        }
    
    def estimate_batch_job_cost(
        self,
        gpu_type: str,
        gpu_count: int,
        estimated_duration_hours: float,
        base_price_per_hour: float
    ) -> Dict[str, Any]:
        """
        Estimate cost for a batch job
        
        Args:
            gpu_type: Type of GPU
            gpu_count: Number of GPUs
            estimated_duration_hours: Estimated duration
            base_price_per_hour: Base price from backend
            
        Returns:
            Cost estimate with markup
        """
        cost_breakdown = self.calculate_instance_cost(
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            duration_hours=estimated_duration_hours,
            base_price_per_hour=base_price_per_hour,
            instance_type="on_demand"
        )
        
        # Add batch job specific calculations
        cost_breakdown.update({
            "minimum_cost": round(cost_breakdown["hourly_rate"] * 0.1, 2),  # Minimum 6 minutes
            "estimated_total": cost_breakdown["total_cost"],
            "maximum_cost": round(cost_breakdown["total_cost"] * 1.2, 2),  # 20% buffer
        })
        
        return cost_breakdown
    
    def calculate_credits_needed(self, usd_amount: float) -> int:
        """
        Calculate credits needed for a USD amount
        1 credit = $0.01 USD with markup
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Number of credits needed
        """
        credits_per_dollar = 100
        return int(usd_amount * credits_per_dollar)
    
    def calculate_usd_from_credits(self, credits: int) -> float:
        """
        Calculate USD value from credits
        
        Args:
            credits: Number of credits
            
        Returns:
            USD value
        """
        credits_per_dollar = 100
        return round(credits / credits_per_dollar, 2)
