#!/usr/bin/env python3
"""
Download and setup MedMNIST dataset.
Lightweight, Mac-friendly dataset for MVP development.

Usage:
    python -m backend.scripts.download_medmnist --dataset chestmnist --subset 1000
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datasets.medmnist_loader import MedMNISTLoader
from datasets.manager import DatasetManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Download and setup MedMNIST dataset"
    )
    parser.add_argument(
        "--dataset",
        choices=["chestmnist", "pathmnist", "dermamnist", "retinamnist", "breastmnist"],
        default="chestmnist",
        help="Which MedMNIST dataset to download"
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Root directory for datasets"
    )
    parser.add_argument(
        "--subset",
        type=int,
        default=None,
        help="Create subset with N samples (optional)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if exists"
    )
    
    args = parser.parse_args()
    
    logger.info(f"🏥 MediScan RAG - MedMNIST Dataset Setup")
    logger.info(f"Dataset: {args.dataset}")
    logger.info(f"Data directory: {args.data_dir}")
    
    # Initialize loader and manager
    loader = MedMNISTLoader(data_dir=f"{args.data_dir}/medmnist")
    manager = DatasetManager(base_dir=args.data_dir)
    
    try:
        # Download dataset
        logger.info(f"⬇️  Downloading {args.dataset}...")
        dataset_path = loader.download_dataset(args.dataset, force=args.force)
        logger.info(f"✅ Downloaded: {dataset_path}")
        
        # Get info
        info = loader.get_dataset_info(args.dataset)
        logger.info(f"📊 Dataset info:")
        logger.info(f"   Description: {info['description']}")
        logger.info(f"   Image size: {info['image_size']}x{info['image_size']}")
        logger.info(f"   Classes: {info['num_classes']}")
        if info['downloaded']:
            logger.info(f"   Size: {info['size_mb']:.2f} MB")
        
        # Create subset if requested
        if args.subset:
            logger.info(f"📦 Creating subset with {args.subset} samples...")
            subset_path = loader.create_subset(
                args.dataset,
                num_samples=args.subset,
                split="train"
            )
            logger.info(f"✅ Subset created: {subset_path}")
            
            dataset_path = subset_path
        
        # Register in dataset manager
        logger.info(f"📝 Registering dataset in manager...")
        manager.register_dataset(
            name=args.dataset,
            version="1.0",
            source="https://medmnist.com/",
            description=info['description'],
            path=str(dataset_path),
            size_gb=info.get('size_mb', 0) / 1024,
            num_samples=args.subset if args.subset else 10000,  # Approximate
            metadata={
                "image_size": info['image_size'],
                "num_classes": info['num_classes'],
            }
        )
        logger.info(f"✅ Dataset registered")
        
        # Show summary
        summary = manager.get_summary()
        logger.info(f"\n📈 Dataset Manager Summary:")
        logger.info(f"   Total datasets: {summary['total_datasets']}")
        logger.info(f"   Total size: {summary['total_size_gb']:.2f} GB")
        logger.info(f"   Total samples: {summary['total_samples']}")
        
        logger.info(f"\n✨ Setup complete! Ready for Phase 1 MVP.")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
