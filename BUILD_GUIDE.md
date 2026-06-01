# MediScan RAG - Complete Build Guide

**Your Path from MVP to Production-Ready System**

---

## 🎯 QUICK REFERENCE

### Current Status
- [x] Project structure
- [x] Docker setup
- [x] Database schema
- [x] Core configuration
- [x] Main app initialized
- [ ] Ready for development

### Before You Start
```bash
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag
source venv/bin/activate  # If you have venv
pip install -r requirements.txt
```

---

## 🚀 PHASE 1: FOUNDATION (Week 1-2)

### Step 1.1: Start Docker Services
**Time: 5 minutes**

```bash
# From project root
docker-compose up -d

# Verify services are running
docker-compose ps

# Should see:
# - postgres (running)
# - qdrant (running)  
# - redis (running)
# - ollama (running)
```

**Troubleshooting:**
```bash
# Check logs
docker-compose logs postgres
docker-compose logs qdrant

# Restart if needed
docker-compose restart

# Full cleanup
docker-compose down -v
docker-compose up -d
```

### Step 1.2: Verify Database Connection
**Time: 5 minutes**

```bash
# Test PostgreSQL connection
psql -h localhost -U mediscan_user -d mediscan_db -c "\dt"

# Expected output: List of relations (tables)
```

### Step 1.3: Initialize Qdrant Collections
**Time: 5 minutes**

```bash
# Create init script
cat > backend/scripts/init_qdrant.py << 'EOF'
import requests
from backend.app.core.config import settings

qdrant_url = settings.QDRANT_URL

# Create medical_documents collection
requests.put(
    f"{qdrant_url}/collections/medical_documents",
    json={
        "vectors": {
            "size": settings.EMBEDDING_DIMENSION,
            "distance": "Cosine",
        }
    }
)

# Create medical_literature collection
requests.put(
    f"{qdrant_url}/collections/medical_literature",
    json={
        "vectors": {
            "size": settings.EMBEDDING_DIMENSION,
            "distance": "Cosine",
        }
    }
)

print("✅ Qdrant collections initialized")
EOF

# Run it
python backend/scripts/init_qdrant.py
```

### Step 1.4: Start Backend
**Time: 10 minutes**

```bash
# Terminal 1: Start FastAPI
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Check it's running:
# Backend should be at: http://localhost:8000
# Docs at: http://localhost:8000/docs
# Redoc at: http://localhost:8000/redoc
```

### Step 1.5: Test Base API
**Time: 5 minutes**

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "database": "connected", ...}

# Test root endpoint
curl http://localhost:8000/

# Expected response:
# {"status": "ok", "message": "...", "app": "MediScan RAG", ...}
```

---

## 👤 PHASE 2: AUTHENTICATION (Week 2-3)

### Step 2.1: Create Auth Service
**Create:** `backend/app/services/auth_service.py`

```python
"""Authentication service - registration, login, token management."""

from sqlalchemy.orm import Session
from backend.app.models.models import User
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.schemas.schemas import UserRegister


class AuthService:
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> User:
        """Register new user."""
        # Check if user exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise ValueError("User already exists")
        
        # Create new user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            name=user_data.name,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def login_user(email: str, password: str, db: Session) -> User:
        """Authenticate user and return user object."""
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        return user
```

### Step 2.2: Create Auth API Endpoints
**Create:** `backend/app/api/auth.py`

```python
"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from backend.app.database.engine import get_db
from backend.app.services.auth_service import AuthService
from backend.app.core.security import create_access_token
from backend.app.core.config import settings
from backend.app.schemas.schemas import (
    UserRegister, UserLogin, UserResponse, TokenResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user."""
    try:
        user = AuthService.register_user(user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    try:
        user = AuthService.login_user(user_data.email, user_data.password, db)
        
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/profile", response_model=UserResponse)
def get_profile(db: Session = Depends(get_db)):
    """Get current user profile. Requires valid JWT token."""
    # This endpoint requires JWT dependency
    # Will implement with middleware
    pass
```

### Step 2.3: Add Auth to Main App
**Update:** `backend/app/main.py`

```python
# Add this after other router imports
from backend.app.api.auth import router as auth_router

# Add this after other include_router calls
app.include_router(auth_router, prefix="/api")
```

### Step 2.4: Test Authentication
**Time: 10 minutes**

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'

# Expected: User created response

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Expected: access_token in response
```

---

## 📄 PHASE 3: DOCUMENT UPLOAD (Week 3-4)

### Step 3.1: Create Document Service
**Create:** `backend/app/services/document_service.py`

```python
"""Document upload and processing service."""

from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.models.models import Document, DocumentChunk
from backend.app.core.config import settings
from uuid import uuid4
import os


class DocumentService:
    @staticmethod
    def save_uploaded_file(file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk."""
        # Create uploads directory if not exists
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        ext = Path(filename).suffix
        unique_filename = f"{uuid4()}{ext}"
        
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return file_path
    
    @staticmethod
    def create_document(
        user_id: str,
        filename: str,
        content_type: str,
        file_path: str,
        extracted_text: str,
        db: Session
    ) -> Document:
        """Create document record in database."""
        document = Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            file_path=file_path,
            extracted_text=extracted_text,
            original_text=extracted_text,
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 100
    ) -> list:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append({
                "text": chunk,
                "start": start,
                "end": end,
            })
            start = end - overlap
        
        return chunks
```

### Step 3.2: Create Document Upload Endpoints
**Create:** `backend/app/api/documents.py`

```python
"""Document management endpoints."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.engine import get_db
from backend.app.services.document_service import DocumentService
from backend.app.schemas.schemas import DocumentResponse
from backend.app.utils.text_processing import extract_text_from_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    # TODO: Add user_id from JWT token
):
    """Upload medical document."""
    
    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.txt', '.md', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported"
        )
    
    # Read file content
    content = await file.read()
    
    # Save file
    file_path = DocumentService.save_uploaded_file(content, file.filename)
    
    # Extract text based on file type
    if file.filename.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = content.decode('utf-8')
    
    # Create document record
    document = DocumentService.create_document(
        user_id="placeholder",  # TODO: Get from JWT
        filename=file.filename,
        content_type=file.content_type,
        file_path=file_path,
        extracted_text=extracted_text,
        db=db,
    )
    
    return document


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    """List user's documents."""
    # TODO: Filter by user_id from JWT
    pass


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, db: Session = Depends(get_db)):
    """Delete document."""
    # TODO: Implement
    pass
```

---

## 🔗 PHASE 4: EMBEDDINGS & VECTOR DB (Week 5-6)

### Step 4.1: Create Embedding Service
**Create:** `backend/app/services/embedding_service.py`

```python
"""Text embedding service using BGE-small."""

from sentence_transformers import SentenceTransformer
from backend.app.core.config import settings


class EmbeddingService:
    def __init__(self):
        """Initialize embedding model."""
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    def embed_text(self, text: str) -> list:
        """Generate embedding for text."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: list) -> list:
        """Generate embeddings for batch of texts."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [e.tolist() for e in embeddings]


# Singleton instance
embedding_service = EmbeddingService()
```

### Step 4.2: Create Qdrant Service
**Create:** `backend/app/services/qdrant_service.py`

```python
"""Qdrant vector database operations."""

from qdrant_client import QdrantClient
from backend.app.core.config import settings
from uuid import uuid4


class QdrantService:
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(url=settings.QDRANT_URL)
    
    def add_point(
        self,
        collection: str,
        vector: list,
        payload: dict,
    ) -> str:
        """Add vector point to collection."""
        point_id = str(uuid4())
        
        self.client.upsert(
            collection_name=collection,
            points=[{
                "id": point_id,
                "vector": vector,
                "payload": payload,
            }]
        )
        
        return point_id
    
    def search(
        self,
        collection: str,
        vector: list,
        limit: int = 5,
    ) -> list:
        """Search for similar vectors."""
        results = self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
        )
        
        return [
            {
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]


# Singleton instance
qdrant_service = QdrantService()
```

---

## 💬 PHASE 6: RAG CHAT SYSTEM (Week 6-8)

### Step 6.1: Create RAG Service
**Create:** `backend/app/services/rag_service.py`

```python
"""RAG (Retrieval-Augmented Generation) service."""

from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from backend.app.core.config import settings
from backend.app.services.embedding_service import embedding_service
from backend.app.services.qdrant_service import qdrant_service


class RAGService:
    def __init__(self):
        """Initialize RAG components."""
        self.llm = Ollama(
            base_url=settings.OLLAMA_URL,
            model=settings.OLLAMA_MODEL,
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a medical knowledge assistant. Based on the following context, 
answer the medical question. Be precise and cite the sources.

Context:
{context}

Question:
{question}

Answer:"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def query(self, question: str, context_docs: list) -> dict:
        """Generate answer from question and context."""
        # Format context
        context = "\n\n".join([
            f"Source: {doc.get('title', 'Unknown')}\n{doc.get('content', '')}"
            for doc in context_docs
        ])
        
        # Generate answer
        answer = self.chain.run(context=context, question=question)
        
        return {
            "answer": answer,
            "sources": [d.get("id") for d in context_docs],
            "context_count": len(context_docs),
        }
    
    def retrieve_context(
        self,
        question: str,
        collection: str = "medical_documents",
        top_k: int = 5
    ) -> list:
        """Retrieve relevant documents for question."""
        # Embed question
        question_embedding = embedding_service.embed_text(question)
        
        # Search in Qdrant
        results = qdrant_service.search(
            collection=collection,
            vector=question_embedding,
            limit=top_k,
        )
        
        return results
```

---

## 🧬 PHASE 7: PUBMED INTEGRATION (Week 8-9)

### Step 7.1: Create PubMed Ingestion Script
**Create:** `backend/scripts/pubmed_ingestor.py`

```python
#!/usr/bin/env python3
"""PubMed literature ingestion pipeline."""

import requests
import time
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database.engine import SessionLocal
from backend.app.models.models import MedicalLiterature
from backend.app.services.embedding_service import embedding_service
from backend.app.services.qdrant_service import qdrant_service


PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOPICS = {
    "pneumonia": "pneumonia AND chest imaging",
    "tuberculosis": "tuberculosis AND radiology",
    "lung_cancer": "lung cancer AND CT",
    "pulmonary_edema": "pulmonary edema",
    "pleural_effusion": "pleural effusion",
}


def search_pubmed(query: str, num_results: int = 100) -> list:
    """Search PubMed for papers."""
    
    # Search for PMIDs
    search_url = f"{PUBMED_API}/esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": num_results,
        "rettype": "json",
    }
    
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    
    pmids = search_data.get("esearchresult", {}).get("idlist", [])
    
    return pmids


def fetch_paper_details(pmid: str) -> dict:
    """Fetch paper details from PubMed."""
    
    fetch_url = f"{PUBMED_API}/efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": pmid,
        "rettype": "json",
    }
    
    fetch_response = requests.get(fetch_url, params=fetch_params)
    data = fetch_response.json()
    
    paper = data.get("result", {}).get(pmid, {})
    
    return {
        "pmid": pmid,
        "title": paper.get("title", ""),
        "abstract": paper.get("abstract", ""),
        "authors": [a.get("name", "") for a in paper.get("authors", [])],
        "journal": paper.get("journal", ""),
        "publication_year": int(paper.get("pubdate", "").split()[-1]) if paper.get("pubdate") else None,
        "doi": paper.get("doi", ""),
        "keywords": paper.get("keywords", []),
    }


def ingest_topic(topic: str, num_papers: int = 100):
    """Ingest papers for a topic."""
    
    print(f"🔍 Searching for {topic} papers...")
    
    query = TOPICS.get(topic)
    pmids = search_pubmed(query, num_papers)
    
    print(f"Found {len(pmids)} papers")
    
    db = SessionLocal()
    
    for i, pmid in enumerate(pmids[:num_papers]):
        print(f"  [{i+1}/{len(pmids)}] Fetching PMID: {pmid}...")
        
        # Check if already exists
        existing = db.query(MedicalLiterature).filter(
            MedicalLiterature.pmid == pmid
        ).first()
        
        if existing:
            print(f"    ⏭️  Already ingested")
            continue
        
        # Fetch paper details
        paper = fetch_paper_details(pmid)
        
        # Create embedding
        title_abstract = f"{paper['title']} {paper['abstract']}"
        embedding = embedding_service.embed_text(title_abstract)
        
        # Add to Qdrant
        embedding_id = qdrant_service.add_point(
            collection="medical_literature",
            vector=embedding,
            payload={
                "pmid": pmid,
                "title": paper["title"],
                "source": "pubmed",
            }
        )
        
        # Save to database
        literature = MedicalLiterature(
            pmid=pmid,
            title=paper["title"],
            abstract=paper["abstract"],
            authors=paper["authors"],
            journal=paper["journal"],
            publication_year=paper["publication_year"],
            doi=paper["doi"],
            keywords=paper["keywords"],
            embedding_id=embedding_id,
            source="pubmed",
            synced_at=datetime.utcnow(),
        )
        
        db.add(literature)
        db.commit()
        
        print(f"    ✅ Ingested")
        
        # Rate limiting
        time.sleep(0.5)
    
    db.close()
    print(f"✅ {topic} ingestion complete")


def ingest_all_topics(num_papers_per_topic: int = 100):
    """Ingest all medical topics."""
    
    for topic in TOPICS.keys():
        try:
            ingest_topic(topic, num_papers_per_topic)
        except Exception as e:
            print(f"❌ Error ingesting {topic}: {e}")


if __name__ == "__main__":
    # Run ingestion
    print("🏥 MediScan - PubMed Ingestion Pipeline")
    print("=" * 50)
    
    ingest_all_topics(num_papers_per_topic=500)
    
    print("\n✨ PubMed ingestion complete!")
```

---

## 📊 COMPLETE IMPLEMENTATION CHECKLIST

### Foundation
- [x] Project structure
- [x] Docker setup
- [x] Database schema
- [ ] Backend running
- [ ] Frontend scaffold

### Authentication
- [ ] Auth service
- [ ] JWT integration
- [ ] Protected routes
- [ ] Login UI
- [ ] Register UI

### Documents
- [ ] Upload endpoint
- [ ] PDF extraction
- [ ] OCR integration
- [ ] Storage
- [ ] Upload UI

### Processing
- [ ] Text chunking
- [ ] Metadata extraction
- [ ] Embedding generation
- [ ] Vector storage

### RAG
- [ ] Embedding service
- [ ] Qdrant integration
- [ ] Retrieval logic
- [ ] Llama integration
- [ ] Chat interface
- [ ] Citation tracking

### Research
- [ ] PubMed API
- [ ] Ingestion pipeline
- [ ] Auto-sync
- [ ] Search UI

### Images
- [ ] ResNet50 setup
- [ ] Training pipeline
- [ ] Inference endpoint
- [ ] Upload UI

### Advanced
- [ ] Multimodal RAG
- [ ] Patient timeline
- [ ] RAGAS evaluation
- [ ] Dashboard

---

## 🔧 UTILITY FILES TO CREATE

### Text Processing Utilities
```bash
# Create backend/app/utils/text_processing.py
# Functions:
# - extract_text_from_pdf()
# - extract_text_from_txt()
# - clean_text()
# - extract_entities()
```

### PDF Handler
```bash
# Create backend/app/utils/pdf_handler.py
# Use: pdf2image, pytesseract, PyPDF2
```

### Logging
```bash
# Create backend/app/utils/logging.py
# Structured logging setup
```

---

## 📈 PERFORMANCE OPTIMIZATION TIPS

1. **Database Indexing:** Add indexes on frequently queried columns
2. **Caching:** Use Redis for chat history and embeddings
3. **Batch Processing:** Embed documents in batches
4. **Rate Limiting:** Add rate limiting to public endpoints
5. **Async Operations:** Use async for I/O operations

---

## 🚀 NEXT STEPS

1. **Immediately:** Verify all Docker services are running
2. **This week:** Complete phases 2-3 (Auth + Documents)
3. **Next week:** Implement embeddings and vector search (Phase 5)
4. **Week 3:** RAG chat system (Phase 6)
5. **Week 4:** PubMed integration (Phase 7)

---

**Start here:** Get all Docker services running
```bash
docker-compose up -d
docker-compose ps
```

All services should show "Up" status. ✨
