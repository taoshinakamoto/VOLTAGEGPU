"""
Instance-related data models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from .gpu import GPUType, Region


class InstanceStatus(str, Enum):
    """Instance status"""
    PENDING = "pending"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    ERROR = "error"
    SUSPENDED = "suspended"


class InstanceType(str, Enum):
    """Instance types"""
    ON_DEMAND = "on_demand"
    SPOT = "spot"
    RESERVED = "reserved"


class ContainerImage(str, Enum):
    """Pre-configured container images"""
    PYTORCH_LATEST = "pytorch:latest"
    PYTORCH_2_0 = "pytorch:2.0"
    TENSORFLOW_LATEST = "tensorflow:latest"
    TENSORFLOW_2_13 = "tensorflow:2.13"
    CUDA_12_2 = "cuda:12.2"
    CUDA_11_8 = "cuda:11.8"
    UBUNTU_22_04 = "ubuntu:22.04"
    CUSTOM = "custom"


class NetworkConfig(BaseModel):
    """Network configuration for instance"""
    public_ip: bool = Field(default=True)
    ipv6_enabled: bool = Field(default=False)
    ports: List[int] = Field(default_factory=lambda: [22, 80, 443, 8888])
    bandwidth_gbps: int = Field(default=10)
    security_groups: List[str] = Field(default_factory=list)


class StorageConfig(BaseModel):
    """Storage configuration for instance"""
    root_disk_size_gb: int = Field(default=100, ge=50, le=10000)
    additional_volumes: List[Dict[str, Any]] = Field(default_factory=list)
    iops: int = Field(default=3000)
    throughput_mbps: int = Field(default=125)
    encrypted: bool = Field(default=True)


class InstanceCreateRequest(BaseModel):
    """Request to create a new instance"""
    name: Optional[str] = Field(None, max_length=255)
    gpu_type: GPUType
    gpu_count: int = Field(default=1, ge=1, le=8)
    region: Region
    image: ContainerImage = Field(default=ContainerImage.PYTORCH_LATEST)
    custom_image: Optional[str] = None
    instance_type: InstanceType = Field(default=InstanceType.ON_DEMAND)
    ssh_key: Optional[str] = None
    user_data: Optional[str] = None
    network_config: Optional[NetworkConfig] = None
    storage_config: Optional[StorageConfig] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    auto_terminate_minutes: Optional[int] = Field(None, ge=5)
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    startup_script: Optional[str] = None


class InstanceInfo(BaseModel):
    """Instance information"""
    id: str = Field(..., description="Unique instance identifier")
    name: str
    status: InstanceStatus
    gpu_type: GPUType
    gpu_count: int
    region: Region
    availability_zone: str
    image: str
    instance_type: InstanceType
    created_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    public_ip: Optional[str] = None
    private_ip: str
    ssh_port: int = Field(default=22)
    ssh_command: Optional[str] = None
    jupyter_url: Optional[str] = None
    monitoring_url: Optional[str] = None
    cost_per_hour: float
    total_cost: float
    runtime_minutes: int
    network_config: NetworkConfig
    storage_config: StorageConfig
    tags: Dict[str, str]
    owner_id: str
    project_id: Optional[str] = None


class InstanceUpdateRequest(BaseModel):
    """Request to update instance configuration"""
    name: Optional[str] = None
    tags: Optional[Dict[str, str]] = None
    auto_terminate_minutes: Optional[int] = None
    network_config: Optional[NetworkConfig] = None


class InstanceActionRequest(BaseModel):
    """Request for instance actions"""
    action: str = Field(..., description="Action to perform: start, stop, restart, terminate")
    force: bool = Field(default=False)
    reason: Optional[str] = None


class InstanceMetrics(BaseModel):
    """Instance metrics"""
    instance_id: str
    timestamp: datetime
    cpu_utilization: float = Field(..., ge=0, le=100)
    memory_utilization: float = Field(..., ge=0, le=100)
    disk_utilization: float = Field(..., ge=0, le=100)
    network_in_mbps: float
    network_out_mbps: float
    gpu_metrics: List[Dict[str, Any]]


class InstanceListResponse(BaseModel):
    """Response for instance listing"""
    instances: List[InstanceInfo]
    total: int
    page: int = Field(default=1)
    per_page: int = Field(default=20)
    filters: Dict[str, Any] = Field(default_factory=dict)


class InstanceConsoleOutput(BaseModel):
    """Console output from instance"""
    instance_id: str
    output: str
    timestamp: datetime
    encoding: str = Field(default="utf-8")


class InstanceSnapshot(BaseModel):
    """Instance snapshot"""
    id: str
    instance_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    size_gb: float
    status: str
    region: Region
    encrypted: bool = Field(default=True)
    tags: Dict[str, str] = Field(default_factory=dict)
