"""
MIMIC-CXR Subset Handler
Multimodal dataset with chest X-rays and radiology reports.
For Phase 2 after MVP is complete.

Dataset: https://physionet.org/content/mimic-cxr-jpg/2.1.0/
Requires PhysioNet credentials.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class MIMICHandler:
    """
    Handler for MIMIC-CXR dataset subset.
    
    Multimodal dataset structure:
    - X-ray images (JPEG)
    - Radiology reports (text)
    - Findings and impressions
    - Patient metadata
    
    MVP recommendation: Start with 1,000-5,000 studies
    """
    
    def __init__(self, data_dir: str = "./data/mimic_cxr"):
        """Initialize MIMIC handler."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.data_dir / "metadata.json"
        self.studies_file = self.data_dir / "studies.jsonl"
    
    def setup_instructions(self) -> Dict[str, str]:
        """
        Return setup instructions for MIMIC-CXR.
        
        MIMIC requires:
        1. PhysioNet account (free but requires registration)
        2. Signed data use agreement
        3. Command-line tools
        """
        return {
            "step_1_register": (
                "1. Register for free account: https://physionet.org/register/\n"
                "2. Sign the data use agreement for MIMIC-CXR-JPG v2.1.0\n"
                "3. Complete CITI training (required)"
            ),
            "step_2_install_tools": (
                "pip install physionet\n"
                "# or use gsutil for Google Cloud\n"
                "pip install gsutil"
            ),
            "step_3_download": (
                "# After credentials approved, download MIMIC-CXR\n"
                "# Option A: Via command line\n"
                "physionet-download --help\n"
                "# Option B: Via web browser (slower)\n"
                "# Download from: https://physionet.org/content/mimic-cxr-jpg/2.1.0/"
            ),
            "step_4_subset": (
                "# For MVP, create subset:\n"
                "python -m backend.scripts.setup_mimic_subset "
                "--num_studies 1000 --output_dir ./data/mimic_cxr_subset"
            ),
        }
    
    def register_study(
        self,
        study_id: str,
        patient_id: str,
        report_text: str,
        findings: str,
        impressions: str,
        image_paths: List[str],
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Register a study in the catalog.
        
        Args:
            study_id: Unique study identifier
            patient_id: Patient identifier
            report_text: Full radiology report
            findings: Extracted findings section
            impressions: Extracted impressions section
            image_paths: Paths to X-ray images
            metadata: Additional metadata
            
        Returns:
            Study record
        """
        study = {
            "study_id": study_id,
            "patient_id": patient_id,
            "report_text": report_text,
            "findings": findings,
            "impressions": impressions,
            "image_paths": image_paths,
            "num_images": len(image_paths),
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        return study
    
    def create_subset(
        self,
        num_studies: int = 1000,
        source_dir: str = "./mimic_cxr_full",
        output_dir: Optional[str] = None,
    ) -> Path:
        """
        Create a subset of MIMIC-CXR for faster experimentation.
        
        Args:
            num_studies: Number of studies to include
            source_dir: Path to full MIMIC-CXR dataset
            output_dir: Where to save subset
            
        Returns:
            Path to subset
        """
        source_path = Path(source_dir)
        
        if not source_path.exists():
            raise ValueError(
                f"Source directory not found: {source_dir}\n"
                f"Please download MIMIC-CXR from: "
                f"https://physionet.org/content/mimic-cxr-jpg/2.1.0/"
            )
        
        if output_dir is None:
            output_dir = self.data_dir / f"subset_{num_studies}"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"Creating MIMIC-CXR subset with {num_studies} studies "
            f"to {output_dir}"
        )
        
        # This would copy/symlink studies from source to subset
        # Implementation depends on MIMIC-CXR directory structure
        
        return output_dir
    
    def load_studies(
        self,
        limit: Optional[int] = None,
    ) -> List[Dict]:
        """Load study records."""
        if not self.studies_file.exists():
            logger.warning(f"Studies file not found: {self.studies_file}")
            return []
        
        studies = []
        with open(self.studies_file, "r") as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                studies.append(json.loads(line))
        
        logger.info(f"Loaded {len(studies)} studies from {self.studies_file}")
        return studies
    
    def create_rag_documents(
        self,
        studies: List[Dict],
    ) -> List[Dict]:
        """
        Convert studies to RAG-compatible documents.
        
        Args:
            studies: List of study records
            
        Returns:
            List of RAG documents
        """
        documents = []
        
        for study in studies:
            # Combine findings and impressions for semantic search
            content = (
                f"Findings: {study.get('findings', '')}\n\n"
                f"Impressions: {study.get('impressions', '')}"
            )
            
            doc = {
                "id": f"mimic_cxr_{study.get('study_id', '')}",
                "title": f"Chest X-ray Study {study.get('study_id', '')}",
                "content": content,
                "metadata": {
                    "source": "mimic_cxr",
                    "study_id": study.get("study_id", ""),
                    "patient_id": study.get("patient_id", ""),
                    "num_images": study.get("num_images", 0),
                    "image_paths": study.get("image_paths", []),
                },
            }
            documents.append(doc)
        
        return documents
    
    def compare_reports(
        self,
        study_id_1: str,
        study_id_2: str,
        studies: List[Dict],
    ) -> Dict:
        """
        Compare two studies (useful for patient timeline feature).
        
        Args:
            study_id_1: First study ID
            study_id_2: Second study ID
            studies: List of study records
            
        Returns:
            Comparison results
        """
        study_map = {s["study_id"]: s for s in studies}
        
        if study_id_1 not in study_map or study_id_2 not in study_map:
            raise ValueError("One or both studies not found")
        
        study1 = study_map[study_id_1]
        study2 = study_map[study_id_2]
        
        comparison = {
            "study_1": study_id_1,
            "study_2": study_id_2,
            "findings_1": study1.get("findings", ""),
            "findings_2": study2.get("findings", ""),
            "impressions_1": study1.get("impressions", ""),
            "impressions_2": study2.get("impressions", ""),
            "num_images_1": study1.get("num_images", 0),
            "num_images_2": study2.get("num_images", 0),
        }
        
        return comparison
