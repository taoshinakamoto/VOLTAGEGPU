"""
Proxy service for forwarding requests to backend provider
"""

import httpx
from typing import Dict, Any, Optional, List
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings


class ProxyService:
    """Service for proxying requests to the backend provider"""
    
    def __init__(self):
        """Initialize the proxy service"""
        self.backend_url = settings.BACKEND_API_URL
        self.backend_api_key = settings.BACKEND_API_KEY
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.headers = {
            "Authorization": f"Bearer {self.backend_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "VoltageGPU/1.0"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def forward_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Forward a request to the backend provider
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Response from the backend provider
        """
        url = f"{self.backend_url}{endpoint}"
        
        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        logger.info(f"Forwarding {method} request to {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                )
                
                response.raise_for_status()
                
                # Log successful request
                logger.info(f"Request successful: {response.status_code}")
                
                return response.json()
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise
    
    async def get_gpu_availability(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get available GPUs from the backend"""
        endpoint = "/gpus/available"
        return await self.forward_request("GET", endpoint, params=filters)
    
    async def create_instance(self, instance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new GPU instance"""
        endpoint = "/compute/instances"
        return await self.forward_request("POST", endpoint, data=instance_data)
    
    async def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """Get instance details"""
        endpoint = f"/compute/instances/{instance_id}"
        return await self.forward_request("GET", endpoint)
    
    async def list_instances(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all instances"""
        endpoint = "/compute/instances"
        return await self.forward_request("GET", endpoint, params=filters)
    
    async def update_instance(self, instance_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update instance configuration"""
        endpoint = f"/compute/instances/{instance_id}"
        return await self.forward_request("PATCH", endpoint, data=update_data)
    
    async def delete_instance(self, instance_id: str) -> Dict[str, Any]:
        """Terminate an instance"""
        endpoint = f"/compute/instances/{instance_id}"
        return await self.forward_request("DELETE", endpoint)
    
    async def instance_action(self, instance_id: str, action: str) -> Dict[str, Any]:
        """Perform an action on an instance (start, stop, restart)"""
        endpoint = f"/compute/instances/{instance_id}/actions"
        return await self.forward_request("POST", endpoint, data={"action": action})
    
    async def get_instance_metrics(self, instance_id: str, period: str = "1h") -> Dict[str, Any]:
        """Get instance metrics"""
        endpoint = f"/compute/instances/{instance_id}/metrics"
        return await self.forward_request("GET", endpoint, params={"period": period})
    
    async def get_instance_logs(self, instance_id: str, lines: int = 100) -> Dict[str, Any]:
        """Get instance console logs"""
        endpoint = f"/compute/instances/{instance_id}/logs"
        return await self.forward_request("GET", endpoint, params={"lines": lines})
    
    async def generate_image(self, generation_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an AI image"""
        endpoint = "/ai/generate/image"
        return await self.forward_request("POST", endpoint, data=generation_params)
    
    async def run_model_inference(self, model_params: Dict[str, Any]) -> Dict[str, Any]:
        """Run model inference"""
        endpoint = "/ai/inference"
        return await self.forward_request("POST", endpoint, data=model_params)
    
    async def submit_batch_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a batch processing job"""
        endpoint = "/batch/jobs"
        return await self.forward_request("POST", endpoint, data=job_data)
    
    async def get_batch_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch job status"""
        endpoint = f"/batch/jobs/{job_id}"
        return await self.forward_request("GET", endpoint)
    
    async def get_pricing_info(self, gpu_type: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
        """Get pricing information from backend"""
        endpoint = "/pricing"
        params = {}
        if gpu_type:
            params["gpu_type"] = gpu_type
        if region:
            params["region"] = region
        return await self.forward_request("GET", endpoint, params=params)
