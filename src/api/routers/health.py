"""
Health Router - Health check endpoint.

ENDPOINTS:
- GET /health - Service health status
"""

from fastapi import APIRouter

# Import models
from ..models import HealthResponse

# Version - should match pyproject.toml or __version__
__version__ = "1.0.0"

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the API service.
    
    Returns:
    - status: healthy/degraded/unhealthy
    - version: API version
    - timestamp: Current server time
    
    **Use cases**:
    - Kubernetes/Load balancer health checks
    - CI/CD deployment verification
    - Uptime monitoring
    - Health dashboards
    """
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
