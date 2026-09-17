"""
Model Registry endpoints.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from ..services.model_registry import get_registry

router = APIRouter(prefix="/models", tags=["Model Registry"])


class PromoteRequest(BaseModel):
    status: str = "production"  # production / staging / archived


@router.get("/", summary="List all model versions")
async def list_models(status: Optional[str] = Query(None, description="Filter by status")):
    """
    Liệt kê tất cả model versions trong registry.
    
    - **status**: Filter (production/staging/archived), None = all
    """
    registry = get_registry()
    versions = registry.list_versions(status=status)
    
    return {
        "current_production": registry.get_production_version(),
        "total_versions": len(versions),
        "versions": [
            {"version": v, **meta}
            for v, meta in versions
        ]
    }


@router.get("/{version}", summary="Get version details")
async def get_version(version: str):
    """
    Lấy metadata chi tiết của 1 version.
    """
    registry = get_registry()
    meta = registry.get_version(version)
    
    if not meta:
        raise HTTPException(status_code=404, detail=f"Version {version} không tồn tại")
    
    return {"version": version, **meta}


@router.get("/compare/{v1}/vs/{v2}", summary="Compare two versions")
async def compare_versions(v1: str, v2: str):
    """
    So sánh metrics giữa 2 versions.
    """
    registry = get_registry()
    
    if not registry.get_version(v1):
        raise HTTPException(status_code=404, detail=f"Version {v1} không tồn tại")
    if not registry.get_version(v2):
        raise HTTPException(status_code=404, detail=f"Version {v2} không tồn tại")
    
    return registry.compare_versions(v1, v2)


@router.post("/{version}/promote", summary="Promote version to new status")
async def promote_version(version: str, request: PromoteRequest):
    """
    Chuyển version sang status mới.
    
    - **status**: production (sẽ archive version cũ) / staging / archived
    """
    registry = get_registry()
    
    try:
        updated = registry.promote_version(version, request.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {
        "version": version,
        "new_status": updated["status"],
        "current_production": registry.get_production_version(),
        "message": f"Version {version} đã chuyển sang {request.status}"
    }
