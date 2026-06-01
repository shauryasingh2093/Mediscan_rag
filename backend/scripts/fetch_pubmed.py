#!/usr/bin/env python3
"""
Fetch PubMed medical research abstracts.
Collect papers on pneumonia, TB, lung cancer, etc.

Requires: pip install biopython

Usage:
    python -m backend.scripts.fetch_pubmed --num-papers 500
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datasets.pubmed_crawler import PubMedCrawler
from datasets.manager import DatasetManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch PubMed medical abstracts"
    )
    parser.add_argument(
        "--num-papers",
        type=int,
        default=500,
        help="Number of papers to fetch per topic"
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Fetch specific topic (or all if None)"
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Root directory for datasets"
    )
    parser.add_argument(
        "--email",
        default="your-email@example.com",
        help="Email for NCBI Entrez API (required for actual fetching)"
    )
    
    args = parser.parse_args()
    
    logger.info(f"🏥 MediScan RAG - PubMed Dataset Fetch")
    logger.info(f"Target papers per topic: {args.num_papers}")
    
    # Initialize crawler and manager
    crawler = PubMedCrawler(data_dir=f"{args.data_dir}/pubmed")
    manager = DatasetManager(base_dir=args.data_dir)
    
    logger.warning(
        "⚠️  PubMed API Setup Required:\n"
        "   1. Install biopython: pip install biopython\n"
        "   2. Set your email in Entrez: Entrez.email = 'your-email@example.com'\n"
        "   3. Get API key (optional): https://www.ncbi.nlm.nih.gov/account/\n"
        "\n   For MVP testing, use mock data or limited queries."
    )
    
    try:
        # Show available topics
        logger.info(f"\n📚 Available topics:")
        for topic, query in crawler.DEFAULT_QUERIES.items():
            logger.info(f"   - {topic}: {query}")
        
        # Fetch papers
        if args.topic and args.topic in crawler.DEFAULT_QUERIES:
            logger.info(f"\n🔍 Fetching {args.topic}...")
            papers = crawler.crawl_topic(args.topic, args.num_papers)
        else:
            logger.info(f"\n🔍 Fetching all topics...")
            papers_by_topic = crawler.crawl_all_topics(args.num_papers)
            papers = [p for topic_papers in papers_by_topic.values() for p in topic_papers]
        
        logger.info(f"✅ Fetched {len(papers)} papers")
        
        if len(papers) == 0:
            logger.warning(
                "⚠️  No papers fetched. This is expected if PubMed API is not configured.\n"
                "   See setup instructions above."
            )
            logger.info("\n📝 Creating mock PubMed data for testing...")
            
            # Create mock data for testing
            papers = [
                {
                    "pmid": f"mock_{i:06d}",
                    "title": f"Mock Study: Medical Topic {i}",
                    "abstract": "This is a mock abstract for testing the RAG pipeline. "
                               f"Sample {i}. In production, this would be fetched from PubMed.",
                    "keywords": ["chest", "medical", "imaging"],
                    "doi": f"10.mock/{i}",
                    "authors": ["Author A", "Author B"],
                    "published_date": "2024-01-01",
                }
                for i in range(min(10, args.num_papers))
            ]
            
            logger.info(f"✅ Created {len(papers)} mock papers for testing")
        
        # Convert to RAG documents
        logger.info(f"\n🔄 Converting to RAG format...")
        documents = crawler.create_rag_documents(papers)
        
        # Save abstracts
        logger.info(f"💾 Saving abstracts...")
        output_file = crawler.save_abstracts(papers)
        logger.info(f"✅ Abstracts saved: {output_file}")
        
        # Register in manager
        logger.info(f"📝 Registering in dataset manager...")
        manager.register_dataset(
            name="pubmed",
            version="1.0",
            source="https://pubmed.ncbi.nlm.nih.gov/",
            description="Medical research abstracts from PubMed",
            path=str(output_file),
            size_gb=sum(len(p.get("abstract", "")) for p in papers) / (1024**3),
            num_samples=len(papers),
            metadata={
                "num_documents": len(documents),
                "topics": list(crawler.DEFAULT_QUERIES.keys()),
            }
        )
        logger.info(f"✅ Dataset registered")
        
        # Show summary
        summary = manager.get_summary()
        logger.info(f"\n📈 Dataset Manager Summary:")
        logger.info(f"   Total datasets: {summary['total_datasets']}")
        logger.info(f"   Total samples: {summary['total_samples']}")
        
        logger.info(f"\n✨ PubMed setup complete!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
