"""
MedMNIST Dataset Loader
Lightweight medical imaging dataset for development and testing.
Small, Mac-friendly, perfect for MVP phase.

Download from: https://medmnist.com/
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import numpy as np

logger = logging.getLogger(__name__)


class MedMNISTLoader:
    """
    Loader for MedMNIST datasets.
    
    Available datasets:
    - PathMNIST (Histopathology)
    - ChestMNIST (Chest X-rays)
    - DermaMNIST (Skin lesions)
    - RetinaMNIST (Fundus images)
    - BreastMNIST (Breast ultrasound)
    """
    
    DATASETS = {
        "pathmnist": {
            "url": "https://zenodo.org/record/5208230/files/pathmnist.npz",
            "description": "Histopathology images",
            "num_classes": 9,
            "image_size": 28,
        },
        "chestmnist": {
            "url": "https://zenodo.org/record/5208230/files/chestmnist.npz",
            "description": "Chest X-ray images",
            "num_classes": 2,
            "image_size": 28,
        },
        "dermamnist": {
            "url": "https://zenodo.org/record/5208230/files/dermamnist.npz",
            "description": "Skin lesion images",
            "num_classes": 10,
            "image_size": 28,
        },
        "retinamnist": {
            "url": "https://zenodo.org/record/5208230/files/retinamnist.npz",
            "description": "Fundus images",
            "num_classes": 5,
            "image_size": 224,
        },
        "breastmnist": {
            "url": "https://zenodo.org/record/5208230/files/breastmnist.npz",
            "description": "Breast ultrasound images",
            "num_classes": 2,
            "image_size": 28,
        },
    }
    
    def __init__(self, data_dir: str = "./data/medmnist"):
        """Initialize MedMNIST loader."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_dataset(
        self,
        dataset_name: str,
        force: bool = False,
    ) -> Path:
        """
        Download a MedMNIST dataset.
        
        Args:
            dataset_name: Name of dataset ('chestmnist', 'pathmnist', etc.)
            force: Force re-download if already exists
            
        Returns:
            Path to downloaded dataset
        """
        if dataset_name not in self.DATASETS:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        dataset_info = self.DATASETS[dataset_name]
        dataset_path = self.data_dir / f"{dataset_name}.npz"
        
        if dataset_path.exists() and not force:
            logger.info(f"Dataset already exists: {dataset_path}")
            return dataset_path
        
        logger.info(f"Downloading {dataset_name} from {dataset_info['url']}...")
        
        try:
            import urllib.request
            urllib.request.urlretrieve(
                dataset_info["url"],
                str(dataset_path),
            )
            logger.info(f"Successfully downloaded: {dataset_path}")
            return dataset_path
        except Exception as e:
            logger.error(f"Failed to download {dataset_name}: {e}")
            raise
    
    def load_dataset(
        self,
        dataset_name: str,
        split: str = "train",
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load a MedMNIST dataset.
        
        Args:
            dataset_name: Name of dataset
            split: 'train', 'val', or 'test'
            
        Returns:
            Tuple of (images, labels)
        """
        dataset_path = self.data_dir / f"{dataset_name}.npz"
        
        if not dataset_path.exists():
            dataset_path = self.download_dataset(dataset_name)
        
        try:
            data = np.load(dataset_path)
            images = data[f"{split}_images"]
            labels = data[f"{split}_labels"].squeeze()
            
            logger.info(
                f"Loaded {dataset_name} {split}: "
                f"{images.shape[0]} images, shape {images.shape[1:]}"
            )
            return images, labels
        except Exception as e:
            logger.error(f"Failed to load {dataset_name}: {e}")
            raise
    
    def get_dataset_info(self, dataset_name: str) -> Dict:
        """Get metadata about a dataset."""
        if dataset_name not in self.DATASETS:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        
        info = self.DATASETS[dataset_name].copy()
        dataset_path = self.data_dir / f"{dataset_name}.npz"
        info["downloaded"] = dataset_path.exists()
        
        if info["downloaded"]:
            size_mb = dataset_path.stat().st_size / (1024 * 1024)
            info["size_mb"] = size_mb
        
        return info
    
    def create_subset(
        self,
        dataset_name: str,
        num_samples: int = 1000,
        split: str = "train",
        output_path: Optional[str] = None,
    ) -> Path:
        """
        Create a subset of a dataset for faster experimentation.
        
        Args:
            dataset_name: Name of dataset
            num_samples: Number of samples to include
            split: Data split to use
            output_path: Where to save subset
            
        Returns:
            Path to subset
        """
        images, labels = self.load_dataset(dataset_name, split)
        
        if num_samples > len(images):
            logger.warning(
                f"Requested {num_samples} samples but only "
                f"{len(images)} available. Using all."
            )
            num_samples = len(images)
        
        indices = np.random.choice(len(images), num_samples, replace=False)
        subset_images = images[indices]
        subset_labels = labels[indices]
        
        if output_path is None:
            output_path = (
                self.data_dir /
                f"{dataset_name}_subset_{num_samples}.npz"
            )
        else:
            output_path = Path(output_path)
        
        np.savez_compressed(
            output_path,
            images=subset_images,
            labels=subset_labels,
        )
        
        logger.info(f"Created subset: {output_path}")
        return output_path
    
    def convert_to_json(
        self,
        dataset_name: str,
        split: str = "train",
        max_samples: Optional[int] = None,
    ) -> List[Dict]:
        """
        Convert dataset to JSON format for ingestion.
        
        Args:
            dataset_name: Name of dataset
            split: Data split
            max_samples: Limit number of samples
            
        Returns:
            List of sample dictionaries
        """
        images, labels = self.load_dataset(dataset_name, split)
        
        if max_samples:
            images = images[:max_samples]
            labels = labels[:max_samples]
        
        dataset_info = self.DATASETS[dataset_name]
        
        samples = []
        for idx, (image, label) in enumerate(zip(images, labels)):
            # Convert image to base64 or save separately
            sample = {
                "id": f"{dataset_name}_{split}_{idx}",
                "dataset": dataset_name,
                "split": split,
                "image_shape": list(image.shape),
                "label": int(label),
                "num_classes": dataset_info["num_classes"],
                "image_size": dataset_info["image_size"],
                "description": f"{dataset_info['description']} - Sample {idx}",
            }
            samples.append(sample)
        
        return samples
