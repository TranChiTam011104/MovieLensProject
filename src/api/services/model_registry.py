"""
Model Registry - Quản lý versions và metadata của models.

FUNCTIONS:
- list_versions(): Liệt kê tất cả versions
- get_version(version): Lấy thông tin 1 version
- get_production_version(): Lấy version đang production
- register_version(): Đăng ký version mới
- promote_version(): Chuyển version sang production/staging/archived
- compare_versions(): So sánh metrics giữa các versions
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil

from ...utils.config import MODELS_DIR, METADATA_FILE


class ModelRegistry:
    """Simple model registry dùng JSON file."""
    
    def __init__(self, metadata_path: Path = None):
        """
        Args:
            metadata_path: Path đến metadata.json file
        """
        self.metadata_path = metadata_path or (MODELS_DIR / METADATA_FILE)
        self._ensure_metadata_exists()
    
    def _ensure_metadata_exists(self):
        """Tạo metadata.json nếu chưa có."""
        if not self.metadata_path.exists():
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_path, 'w') as f:
                json.dump({
                    "current_production": None,
                    "models": {}
                }, f, indent=2)
    
    def _load(self) -> dict:
        """Load metadata từ file."""
        with open(self.metadata_path, 'r') as f:
            return json.load(f)
    
    def _save(self, data: dict):
        """Save metadata vào file."""
        with open(self.metadata_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def list_versions(self, status: Optional[str] = None) -> list:
        """
        Liệt kê tất cả versions.
        
        Args:
            status: Filter theo status (production/staging/archived/None=all)
            
        Returns:
            List of (version, metadata) tuples
        """
        data = self._load()
        versions = []
        for version, meta in data.get("models", {}).items():
            if status is None or meta.get("status") == status:
                versions.append((version, meta))
        return versions
    
    def get_version(self, version: str) -> Optional[dict]:
        """
        Lấy metadata của 1 version.
        
        Args:
            version: Version name (e.g., "v1.0")
            
        Returns:
            Metadata dict hoặc None nếu không tìm thấy
        """
        data = self._load()
        return data.get("models", {}).get(version)
    
    def get_production_version(self) -> Optional[str]:
        """Lấy version đang production."""
        data = self._load()
        return data.get("current_production")
    
    def register_version(
        self,
        version: str,
        model_name: str,
        file_path: str,
        metrics: dict = None,
        hyperparameters: dict = None,
        data_info: dict = None,
        description: str = ""
    ) -> dict:
        """
        Đăng ký version mới.
        
        Args:
            version: Tên version (e.g., "v1.1")
            model_name: Tên model (e.g., "svd_model_full")
            file_path: Path đến model file (relative to project root)
            metrics: Dict chứa metrics (rmse, mae, etc.)
            hyperparameters: Dict chứa hyperparameters
            data_info: Dict chứa info về data
            description: Mô tả về version này
            
        Returns:
            Metadata của version vừa register
        """
        data = self._load()
        
        if version in data.get("models", {}):
            raise ValueError(f"Version {version} đã tồn tại!")
        
        new_meta = {
            "model_name": model_name,
            "file_path": file_path,
            "trained_at": datetime.utcnow().isoformat() + "Z",
            "status": "staging",  # Mặc định là staging
            "metrics": metrics or {},
            "hyperparameters": hyperparameters or {},
            "data": data_info or {},
            "description": description
        }
        
        if "models" not in data:
            data["models"] = {}
        data["models"][version] = new_meta
        self._save(data)
        
        return new_meta
    
    def promote_version(self, version: str, new_status: str = "production") -> dict:
        """
        Chuyển version sang status mới.
        
        Args:
            version: Version name
            new_status: "production" / "staging" / "archived"
            
        Returns:
            Updated metadata
        """
        if new_status not in ["production", "staging", "archived"]:
            raise ValueError(f"Invalid status: {new_status}")
        
        data = self._load()
        
        if version not in data.get("models", {}):
            raise ValueError(f"Version {version} không tồn tại!")
        
        # Nếu promote to production, archive version cũ
        if new_status == "production":
            old_prod = data.get("current_production")
            if old_prod and old_prod in data["models"]:
                data["models"][old_prod]["status"] = "archived"
            data["current_production"] = version
        
        data["models"][version]["status"] = new_status
        self._save(data)
        
        return data["models"][version]
    
    def compare_versions(self, version1: str, version2: str) -> dict:
        """
        So sánh metrics giữa 2 versions.
        
        Returns:
            Dict chứa metrics của cả 2 và delta
        """
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        if not v1 or not v2:
            raise ValueError("Version không tồn tại")
        
        comparison = {
            "version_1": {"version": version1, "metrics": v1.get("metrics", {})},
            "version_2": {"version": version2, "metrics": v2.get("metrics", {})},
            "delta": {}
        }
        
        # Tính delta cho từng metric
        for metric in v1.get("metrics", {}):
            if metric in v2.get("metrics", {}):
                delta = v2["metrics"][metric] - v1["metrics"][metric]
                comparison["delta"][metric] = round(delta, 4)
        
        return comparison


# Singleton instance
_registry = None

def get_registry() -> ModelRegistry:
    """Get global registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
