"""
Dataset Manager - Centralized management for all datasets.
Handles versioning, caching, preprocessing, and metadata tracking.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DatasetManager:
    """Manages dataset lifecycle: download, preprocess, version, and catalog."""
    
    def __init__(self, base_dir: str = "./data"):
        """
        Initialize Dataset Manager.
        
        Args:
            base_dir: Root directory for all datasets
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.base_dir / "datasets_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load or initialize metadata file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {"datasets": {}, "last_updated": None}
    
    def _save_metadata(self) -> None:
        """Save metadata to file."""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def register_dataset(
        self,
        name: str,
        version: str,
        source: str,
        description: str,
        path: str,
        size_gb: float,
        num_samples: int,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Register a dataset in the catalog.
        
        Args:
            name: Dataset name (e.g., 'medmnist')
            version: Version (e.g., '1.0')
            source: Source URL or reference
            description: Human-readable description
            path: Local path to dataset
            size_gb: Size in GB
            num_samples: Number of samples/records
            metadata: Additional metadata
        """
        dataset_key = f"{name}_{version}"
        
        self.metadata["datasets"][dataset_key] = {
            "name": name,
            "version": version,
            "source": source,
            "description": description,
            "path": path,
            "size_gb": size_gb,
            "num_samples": num_samples,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        self._save_metadata()
        logger.info(f"Registered dataset: {dataset_key}")
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all registered datasets."""
        return list(self.metadata["datasets"].values())
    
    def get_dataset_info(self, name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific dataset."""
        dataset_key = f"{name}_{version}"
        return self.metadata["datasets"].get(dataset_key)
    
    def get_dataset_path(self, name: str, version: str = "latest") -> Optional[Path]:
        """Get path to a dataset."""
        if version == "latest":
            # Find latest version of dataset
            matching = [
                (k, v) for k, v in self.metadata["datasets"].items()
                if v["name"] == name
            ]
            if not matching:
                return None
            # Sort by registered_at and get latest
            matching.sort(key=lambda x: x[1]["registered_at"], reverse=True)
            path = matching[0][1]["path"]
        else:
            info = self.get_dataset_info(name, version)
            if not info:
                return None
            path = info["path"]
        
        return Path(path) if path else None
    
    def validate_dataset(self, name: str, version: str = "latest") -> bool:
        """Check if dataset files exist."""
        path = self.get_dataset_path(name, version)
        if not path:
            return False
        return path.exists() and (path.is_dir() or path.is_file())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all registered datasets."""
        datasets = self.metadata["datasets"]
        
        return {
            "total_datasets": len(datasets),
            "total_size_gb": sum(d.get("size_gb", 0) for d in datasets.values()),
            "total_samples": sum(d.get("num_samples", 0) for d in datasets.values()),
            "datasets": {
                d["name"]: {
                    "versions": len([x for x in datasets.values() if x["name"] == d["name"]]),
                    "total_samples": d["num_samples"],
                    "size_gb": d["size_gb"],
                }
                for d in list(datasets.values())
            },
        }
