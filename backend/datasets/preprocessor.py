"""
Data Preprocessing Utilities
Convert raw datasets to RAG-compatible format for ingestion.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Utilities for preprocessing datasets for RAG ingestion."""
    
    @staticmethod
    def create_rag_document(
        doc_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict] = None,
        source: str = "unknown",
    ) -> Dict:
        """
        Create a standardized RAG document.
        
        Args:
            doc_id: Unique document ID
            title: Document title
            content: Full document content/text
            metadata: Additional metadata
            source: Data source
            
        Returns:
            RAG-compatible document dict
        """
        return {
            "id": doc_id,
            "title": title,
            "content": content,
            "source": source,
            "metadata": metadata or {},
        }
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 512,
        overlap: int = 50,
    ) -> List[str]:
        """
        Chunk text for embedding with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def extract_medical_entities(text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from text.
        
        Simple regex-based extraction. For production, use:
        - spaCy with medical models
        - SciBERT
        - BioBERT
        
        Args:
            text: Medical text
            
        Returns:
            Dict of extracted entities
        """
        import re
        
        entities = {
            "diseases": [],
            "medications": [],
            "procedures": [],
            "symptoms": [],
        }
        
        # Simple patterns - these are just examples
        # In production, use proper NER models
        disease_pattern = r'\b(?:pneumonia|tuberculosis|cancer|diabetes|hypertension)\b'
        symptom_pattern = r'\b(?:fever|cough|dyspnea|chest pain|fatigue)\b'
        
        entities["diseases"] = list(set(
            re.findall(disease_pattern, text, re.IGNORECASE)
        ))
        entities["symptoms"] = list(set(
            re.findall(symptom_pattern, text, re.IGNORECASE)
        ))
        
        return entities
    
    @staticmethod
    def clean_medical_text(text: str) -> str:
        """
        Clean and normalize medical text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        import re
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep medical punctuation
        text = re.sub(r'[^\w\s\-\./()%°]', '', text)
        
        # Normalize common medical abbreviations
        normalizations = {
            r'\bPT\b': 'patient',
            r'\bMR\b': 'magnetic resonance',
            r'\bCT\b': 'computed tomography',
        }
        
        for pattern, replacement in normalizations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def create_document_batch(
        documents: List[Dict],
        output_file: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Save a batch of documents in JSONL format.
        
        Args:
            documents: List of document dicts
            output_file: Output file path
            
        Returns:
            Path to file if output_file provided, else None
        """
        if output_file is None:
            return None
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            for doc in documents:
                f.write(json.dumps(doc) + "\n")
        
        logger.info(f"Saved {len(documents)} documents to {output_path}")
        return output_path
    
    @staticmethod
    def load_document_batch(file_path: str) -> List[Dict]:
        """
        Load documents from JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of documents
        """
        documents = []
        
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():
                    documents.append(json.loads(line))
        
        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents
    
    @staticmethod
    def validate_rag_document(doc: Dict) -> bool:
        """
        Validate document has required RAG fields.
        
        Required fields:
        - id
        - title
        - content
        
        Args:
            doc: Document to validate
            
        Returns:
            True if valid
        """
        required_fields = ["id", "title", "content"]
        return all(field in doc and doc[field] for field in required_fields)
