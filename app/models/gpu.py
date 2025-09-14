"""
GPU-related data models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class GPUType(str, Enum):
    """Available GPU types"""
    RTX_4090 = "RTX_4090"
    RTX_4080 = "RTX_4080"
    RTX_4070 = "RTX_4070"
    RTX_3090 = "RTX_3090"
    RTX_3080 = "RTX_3080"
    RTX_3070 = "RTX_3070"
    A100 = "A100"
    A40 = "A40"
    A30 = "A30"
    A10 = "A10"
    H100 = "H100"
    H200 = "H200"
    L40 = "L40"
    L4 = "L4"
    T4 = "T4"
    V100 = "V100"


class GPUStatus(str, Enum):
    """GPU availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class Region(str, Enum):
    """Available regions"""
    US_EAST_1 = "us-east-1"
    US_WEST_1 = "us-west-1"
    US_CENTRAL_1 = "us-central-1"
    EU_WEST_1 = "eu-west-1"
    EU_CENTRAL_1 = "eu-central-1"
    AP_NORTHEAST_1 = "ap-northeast-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"


class GPUSpecs(BaseModel):
    """GPU specifications"""
    name: str
    vram: int = Field(..., description="VRAM in GB")
    memory_bandwidth: int = Field(..., description="Memory bandwidth in GB/s")
    fp32_tflops: float = Field(..., description="FP32 performance in TFLOPS")
    fp16_tflops: float = Field(..., description="FP16 performance in TFLOPS")
    cuda_cores: Optional[int] = None
    tensor_cores: Optional[int] = None
    architecture: str
    tdp: int = Field(..., description="TDP in watts")


class GPUInfo(BaseModel):
    """GPU information"""
    id: str = Field(..., description="Unique GPU identifier")
    type: GPUType
    specs: GPUSpecs
    status: GPUStatus
    region: Region
    availability_zones: List[str]
    price_per_hour: float = Field(..., description="Price in USD per hour")
    price_per_minute: float = Field(..., description="Price in USD per minute")
    minimum_rental_minutes: int = Field(default=5)
    maximum_rental_hours: int = Field(default=720)  # 30 days
    available_count: int
    total_count: int
    features: List[str] = Field(default_factory=list)
    supported_frameworks: List[str] = Field(
        default_factory=lambda: ["PyTorch", "TensorFlow", "JAX", "CUDA"]
    )
    

class GPUAllocation(BaseModel):
    """GPU allocation request"""
    gpu_type: GPUType
    gpu_count: int = Field(default=1, ge=1, le=8)
    region: Region
    duration_minutes: Optional[int] = Field(None, ge=5)
    spot_instance: bool = Field(default=False)
    reserved_instance: bool = Field(default=False)


class GPUMetrics(BaseModel):
    """GPU metrics and monitoring data"""
    gpu_id: str
    timestamp: datetime
    utilization: float = Field(..., ge=0, le=100, description="GPU utilization percentage")
    memory_used: int = Field(..., description="Memory used in MB")
    memory_total: int = Field(..., description="Total memory in MB")
    temperature: float = Field(..., description="Temperature in Celsius")
    power_draw: float = Field(..., description="Power draw in watts")
    fan_speed: Optional[float] = Field(None, description="Fan speed percentage")
    compute_mode: str = Field(default="Default")
    processes: List[Dict[str, Any]] = Field(default_factory=list)


class GPUListResponse(BaseModel):
    """Response for GPU listing"""
    gpus: List[GPUInfo]
    total: int
    page: int = Field(default=1)
    per_page: int = Field(default=20)
    filters: Dict[str, Any] = Field(default_factory=dict)


class GPUAvailability(BaseModel):
    """GPU availability information"""
    gpu_type: GPUType
    region: Region
    available: int
    total: int
    next_available: Optional[datetime] = None
    average_wait_time_minutes: Optional[int] = None
    spot_available: bool = False
    spot_price: Optional[float] = None
