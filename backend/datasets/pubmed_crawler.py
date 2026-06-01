"""
PubMed Crawler - Fetch medical research abstracts.
Collects relevant papers on specific medical topics.

PubMed API: https://pubmed.ncbi.nlm.nih.gov/
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class PubMedCrawler:
    """
    Crawler for PubMed medical literature abstracts.
    
    Target topics for MVP:
    - Pneumonia
    - Tuberculosis
    - Lung cancer
    - Pulmonary edema
    - Pleural effusion
    """
    
    BASE_URL = "https://pubmed.ncbi.nlm.nih.gov/api/search"
    
    DEFAULT_QUERIES = {
        "pneumonia": "pneumonia AND chest x-ray",
        "tuberculosis": "tuberculosis AND imaging",
        "lung_cancer": "lung cancer AND CT",
        "pulmonary_edema": "pulmonary edema",
        "pleural_effusion": "pleural effusion",
    }
    
    def __init__(self, data_dir: str = "./data/pubmed"):
        """Initialize PubMed crawler."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.abstracts_file = self.data_dir / "abstracts.jsonl"
    
    def search_papers(
        self,
        query: str,
        num_results: int = 100,
        retstart: int = 0,
    ) -> List[Dict]:
        """
        Search PubMed for papers.
        
        Note: This is a template. Actual implementation requires:
        - PubMed API key (optional but recommended)
        - Proper rate limiting
        - Error handling
        
        Args:
            query: Search query
            num_results: Number of results to fetch
            retstart: Starting position for pagination
            
        Returns:
            List of paper metadata
        """
        logger.info(f"Searching PubMed for: {query}")
        
        # In production, use biopython or direct API calls:
        # from Bio import Entrez
        # Entrez.email = "your-email@example.com"
        # handle = Entrez.esearch(db="pubmed", term=query, retmax=num_results)
        
        # For now, return template structure
        papers = []
        
        logger.warning(
            "PubMed API search requires setup. "
            "Use biopython: pip install biopython"
        )
        
        return papers
    
    def fetch_abstract(self, pmid: str) -> Optional[Dict]:
        """
        Fetch full abstract details for a paper.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Paper metadata with abstract
        """
        # Template for actual PubMed API call
        logger.debug(f"Fetching abstract for PMID: {pmid}")
        
        paper = {
            "pmid": pmid,
            "title": "",
            "abstract": "",
            "authors": [],
            "published_date": "",
            "keywords": [],
            "doi": "",
        }
        
        return paper
    
    def crawl_topic(
        self,
        topic: str,
        num_papers: int = 500,
    ) -> List[Dict]:
        """
        Crawl papers for a specific medical topic.
        
        Args:
            topic: Topic name (from DEFAULT_QUERIES)
            num_papers: Number of papers to fetch
            
        Returns:
            List of papers
        """
        if topic not in self.DEFAULT_QUERIES:
            raise ValueError(
                f"Unknown topic. Available: {list(self.DEFAULT_QUERIES.keys())}"
            )
        
        query = self.DEFAULT_QUERIES[topic]
        logger.info(f"Crawling topic '{topic}' with query: {query}")
        
        papers = []
        batch_size = 100
        
        for offset in range(0, num_papers, batch_size):
            batch_papers = self.search_papers(
                query,
                num_results=min(batch_size, num_papers - offset),
                retstart=offset,
            )
            papers.extend(batch_papers)
            
            # Rate limiting
            if offset + batch_size < num_papers:
                time.sleep(1)  # Be respectful to PubMed servers
        
        logger.info(f"Fetched {len(papers)} papers for topic: {topic}")
        return papers
    
    def crawl_all_topics(
        self,
        papers_per_topic: int = 100,
    ) -> Dict[str, List[Dict]]:
        """
        Crawl all default medical topics.
        
        Args:
            papers_per_topic: Papers to fetch per topic
            
        Returns:
            Dict mapping topic to papers
        """
        all_papers = {}
        
        for topic in self.DEFAULT_QUERIES.keys():
            try:
                papers = self.crawl_topic(topic, papers_per_topic)
                all_papers[topic] = papers
            except Exception as e:
                logger.error(f"Failed to crawl {topic}: {e}")
                all_papers[topic] = []
        
        return all_papers
    
    def save_abstracts(
        self,
        papers: List[Dict],
        output_file: Optional[str] = None,
    ) -> Path:
        """
        Save abstracts in JSONL format for RAG ingestion.
        
        Args:
            papers: List of paper metadata
            output_file: Output file path
            
        Returns:
            Path to saved file
        """
        if output_file is None:
            output_file = self.abstracts_file
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            for paper in papers:
                f.write(json.dumps({
                    "id": paper.get("pmid", ""),
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "keywords": paper.get("keywords", []),
                    "doi": paper.get("doi", ""),
                    "authors": paper.get("authors", []),
                    "published_date": paper.get("published_date", ""),
                    "source": "pubmed",
                }) + "\n")
        
        logger.info(f"Saved {len(papers)} abstracts to {output_file}")
        return output_file
    
    def load_abstracts(
        self,
        file_path: Optional[str] = None,
    ) -> List[Dict]:
        """Load saved abstracts."""
        if file_path is None:
            file_path = self.abstracts_file
        else:
            file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Abstracts file not found: {file_path}")
            return []
        
        papers = []
        with open(file_path, "r") as f:
            for line in f:
                papers.append(json.loads(line))
        
        logger.info(f"Loaded {len(papers)} abstracts from {file_path}")
        return papers
    
    def create_rag_documents(
        self,
        papers: List[Dict],
    ) -> List[Dict]:
        """
        Convert papers to RAG-compatible document format.
        
        Args:
            papers: List of paper metadata
            
        Returns:
            List of RAG documents
        """
        documents = []
        
        for paper in papers:
            doc = {
                "id": f"pubmed_{paper.get('pmid', '')}",
                "title": paper.get("title", ""),
                "content": f"Title: {paper.get('title', '')}\n\n"
                          f"Abstract: {paper.get('abstract', '')}\n\n"
                          f"Keywords: {', '.join(paper.get('keywords', []))}",
                "metadata": {
                    "source": "pubmed",
                    "pmid": paper.get("pmid", ""),
                    "doi": paper.get("doi", ""),
                    "published_date": paper.get("published_date", ""),
                    "authors": paper.get("authors", []),
                },
            }
            documents.append(doc)
        
        return documents
