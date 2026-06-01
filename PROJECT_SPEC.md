# MediScan RAG - Complete Production Implementation Guide

**Status:** Phase 1 - Foundation Setup  
**Target:** Production-Ready Multimodal Medical Intelligence Assistant  
**Timeline:** 12-16 weeks for complete implementation

---

## 📋 PROJECT OVERVIEW

### What is MediScan?
A production-grade AI-powered medical intelligence system that:
- ✅ Processes medical reports & documents (OCR + NLP)
- ✅ Retrieves relevant medical research (PubMed integration)
- ✅ Analyzes medical images (Chest X-rays)
- ✅ Provides citation-grounded answers (RAG)
- ✅ Tracks patient progression (timelines)
- ✅ Explains medical concepts in plain language

### NOT a Diagnostic Tool
This is a **medical knowledge & document intelligence platform**, not a diagnostic system. It helps organize and understand medical information.

---

## 🏗️ TECH STACK

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Vector DB:** Qdrant
- **Embeddings:** BAAI/bge-small-en-v1.5
- **LLM:** Llama 3 8B (via Ollama)
- **RAG:** LangChain
- **Auth:** JWT

### Frontend
- **Framework:** Next.js 15
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** ShadCN UI

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **AI Runtime:** Ollama (Llama 3)

---

## 📊 DATABASE SCHEMA

### Core Tables

```sql
-- Users & Authentication
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR,
  name VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Document Management
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  filename VARCHAR,
  content_type VARCHAR,
  file_path VARCHAR,
  original_text TEXT,
  extracted_text TEXT,
  metadata JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE document_chunks (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  chunk_text TEXT,
  chunk_number INT,
  start_char INT,
  end_char INT,
  embedding_id UUID,
  metadata JSONB,
  created_at TIMESTAMP
);

-- Medical Literature
CREATE TABLE medical_literature (
  id UUID PRIMARY KEY,
  pmid VARCHAR UNIQUE,
  title VARCHAR,
  abstract TEXT,
  authors VARCHAR[],
  journal VARCHAR,
  publication_year INT,
  doi VARCHAR,
  keywords VARCHAR[],
  embedding_id UUID,
  source VARCHAR,
  synced_at TIMESTAMP,
  created_at TIMESTAMP
);

-- Chat System
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  patient_id UUID,
  title VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE messages (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES chat_sessions(id),
  role VARCHAR (user/assistant),
  content TEXT,
  sources JSONB,
  metadata JSONB,
  created_at TIMESTAMP
);

-- Image Analysis
CREATE TABLE image_findings (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  image_path VARCHAR,
  prediction VARCHAR,
  confidence FLOAT,
  findings TEXT,
  model_version VARCHAR,
  created_at TIMESTAMP
);

-- Patient Timeline
CREATE TABLE patient_timeline (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  patient_name VARCHAR,
  event_date TIMESTAMP,
  event_type VARCHAR (report/image/note),
  content TEXT,
  associated_documents UUID[],
  summary TEXT,
  created_at TIMESTAMP
);
```

---

## 🗂️ PROJECT STRUCTURE

```
mediscan-rag/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── documents.py         # Document upload/management
│   │   │   ├── chat.py              # RAG chat endpoints
│   │   │   ├── literature.py        # PubMed search
│   │   │   ├── images.py            # X-ray analysis
│   │   │   ├── timeline.py          # Patient timeline
│   │   │   └── dashboard.py         # Statistics
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # JWT, password hashing
│   │   │   ├── document_service.py  # Upload, OCR, storage
│   │   │   ├── embedding_service.py # Text embeddings
│   │   │   ├── qdrant_service.py    # Vector DB operations
│   │   │   ├── rag_service.py       # RAG logic
│   │   │   ├── literature_service.py # PubMed integration
│   │   │   ├── image_service.py     # X-ray analysis
│   │   │   └── evaluation_service.py # RAGAS metrics
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── chat.py
│   │   │   ├── literature.py
│   │   │   └── image.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # Pydantic schemas
│   │   │   ├── document.py
│   │   │   ├── chat.py
│   │   │   └── literature.py
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py            # PostgreSQL setup
│   │   │   ├── base.py              # SQLAlchemy Base
│   │   │   └── init_db.py           # Schema creation
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Environment variables
│   │   │   ├── security.py          # JWT, hashing
│   │   │   └── constants.py
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── text_processing.py   # Chunking, cleaning
│   │   │   ├── pdf_handler.py       # PDF extraction
│   │   │   ├── logging.py
│   │   │   └── validators.py
│   │   │
│   │   └── main.py                  # FastAPI app
│   │
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── setup_datasets.py        # Dataset initialization
│   │   ├── pubmed_ingestor.py       # PubMed crawler
│   │   ├── train_xray_model.py      # Train classifier
│   │   ├── init_qdrant.py           # Qdrant collections
│   │   └── evaluate_rag.py          # RAGAS evaluation
│   │
│   ├── ml_models/
│   │   ├── __init__.py
│   │   ├── xray_classifier.py       # ResNet50 model
│   │   └── models/
│   │       └── xray_model_v1.pth    # Trained weights
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_rag.py
│       ├── test_literature.py
│       └── fixtures.py
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Home page
│   │   │
│   │   ├── auth/
│   │   │   ├── page.tsx             # Auth pages
│   │   │   ├── login/
│   │   │   └── register/
│   │   │
│   │   ├── documents/
│   │   │   ├── page.tsx             # Document list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx         # Document detail
│   │   │   └── upload/
│   │   │       └── page.tsx         # Upload page
│   │   │
│   │   ├── chat/
│   │   │   ├── page.tsx             # Chat page
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Chat session
│   │   │
│   │   ├── literature/
│   │   │   ├── page.tsx             # Literature search
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Paper detail
│   │   │
│   │   ├── images/
│   │   │   └── page.tsx             # X-ray analysis
│   │   │
│   │   ├── timeline/
│   │   │   └── page.tsx             # Patient timeline
│   │   │
│   │   └── dashboard/
│   │       └── page.tsx             # Statistics
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   │
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Loading.tsx
│   │   │   └── Error.tsx
│   │   │
│   │   ├── features/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── LiteratureSearch.tsx
│   │   │   ├── ImageAnalyzer.tsx
│   │   │   └── Timeline.tsx
│   │   │
│   │   └── forms/
│   │       ├── LoginForm.tsx
│   │       ├── RegisterForm.tsx
│   │       └── UploadForm.tsx
│   │
│   ├── hooks/
│   │   ├── useAuth.ts               # Auth context
│   │   ├── useApi.ts                # API calls
│   │   ├── useChat.ts               # Chat state
│   │   └── useDocument.ts           # Document state
│   │
│   ├── services/
│   │   ├── api.ts                   # Axios/Fetch setup
│   │   ├── auth.ts                  # Auth API calls
│   │   ├── documents.ts             # Document API calls
│   │   ├── chat.ts                  # Chat API calls
│   │   ├── literature.ts            # Literature API calls
│   │   └── images.ts                # Image API calls
│   │
│   ├── types/
│   │   ├── index.ts
│   │   ├── auth.ts
│   │   ├── document.ts
│   │   ├── chat.ts
│   │   └── literature.ts
│   │
│   ├── lib/
│   │   ├── utils.ts
│   │   └── constants.ts
│   │
│   ├── public/
│   │   ├── images/
│   │   ├── icons/
│   │   └── logos/
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   └── variables.css
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   └── tailwind.config.js
│
├── docker-compose.yml               # All services
├── .env.example
├── requirements.txt                 # Python dependencies
├── package.json                     # Frontend root dependencies
├── README.md
└── DEPLOYMENT.md
```

---

## 🔄 IMPLEMENTATION PHASES

### Phase 1: Foundation (Week 1-2)
- [x] Project structure setup
- [x] Docker configuration
- [x] PostgreSQL + Qdrant setup
- [ ] FastAPI skeleton
- [ ] Next.js setup
- [ ] Database migrations
- [ ] Basic routing

**Deliverable:** Running FastAPI + Next.js + PostgreSQL + Qdrant

### Phase 2: Authentication (Week 2-3)
- [ ] User model
- [ ] JWT implementation
- [ ] Register endpoint
- [ ] Login endpoint
- [ ] Protected routes
- [ ] Frontend auth UI

**Deliverable:** Working login/register with JWT

### Phase 3: Document Upload (Week 3-4)
- [ ] Document model
- [ ] Upload endpoint
- [ ] PDF/TXT parsing
- [ ] OCR integration (Tesseract)
- [ ] Text extraction
- [ ] File storage
- [ ] Frontend upload UI

**Deliverable:** Users can upload and extract text from documents

### Phase 4: Text Processing (Week 4-5)
- [ ] Text chunking logic
- [ ] Metadata extraction
- [ ] Document cleaning
- [ ] Storage in PostgreSQL
- [ ] Chunk management

**Deliverable:** Documents chunked and stored in DB

### Phase 5: Embeddings & Vector DB (Week 5-6)
- [ ] Embedding service (BGE-small)
- [ ] Qdrant collection setup
- [ ] Batch embedding
- [ ] Vector storage
- [ ] Similarity search

**Deliverable:** Documents can be searched semantically

### Phase 6: RAG Chat System (Week 6-8)
- [ ] Llama 3 integration (Ollama)
- [ ] Retrieval logic
- [ ] Prompt engineering
- [ ] Response generation
- [ ] Citation tracking
- [ ] Chat history
- [ ] Streaming responses
- [ ] Chat UI

**Deliverable:** Users can chat with uploaded documents

### Phase 7: PubMed Integration (Week 8-9)
- [ ] PubMed API integration
- [ ] Paper fetching
- [ ] Metadata extraction
- [ ] Embedding papers
- [ ] Vector storage
- [ ] Auto-sync scheduler
- [ ] Search UI

**Deliverable:** Access to latest medical research

### Phase 8: X-Ray Analysis (Week 9-10)
- [ ] ResNet50 model setup
- [ ] Training pipeline
- [ ] Model evaluation
- [ ] Inference endpoint
- [ ] Result storage
- [ ] Prediction UI

**Deliverable:** Users can upload X-rays and get predictions

### Phase 9: Multimodal Integration (Week 10-11)
- [ ] Report + Image combination
- [ ] Context-aware retrieval
- [ ] Cross-modal search
- [ ] Enhanced RAG

**Deliverable:** Ask about reports AND images together

### Phase 10: Patient Timeline (Week 11-12)
- [ ] Timeline model
- [ ] Event tracking
- [ ] Progression analysis
- [ ] AI summarization
- [ ] Timeline UI

**Deliverable:** View patient progression over time

### Phase 11: Evaluation Dashboard (Week 12-13)
- [ ] RAGAS metrics
- [ ] Faithfulness scoring
- [ ] Answer relevance
- [ ] Context precision
- [ ] Dashboard UI

**Deliverable:** Measure and display RAG quality

### Phase 12: Deployment (Week 13-16)
- [ ] Docker production setup
- [ ] Environment configuration
- [ ] SSL certificates
- [ ] Database backups
- [ ] Monitoring setup
- [ ] Performance optimization
- [ ] Documentation

**Deliverable:** Production-ready system

---

## 🚀 API ENDPOINTS SPEC

### Authentication
```
POST   /api/auth/register              Register new user
POST   /api/auth/login                 Login user
GET    /api/auth/profile               Get user profile (protected)
POST   /api/auth/logout                Logout (protected)
POST   /api/auth/refresh               Refresh token
```

### Documents
```
POST   /api/documents                  Upload document (protected)
GET    /api/documents                  List documents (protected)
GET    /api/documents/{id}             Get document detail (protected)
DELETE /api/documents/{id}             Delete document (protected)
GET    /api/documents/{id}/preview     Get document preview (protected)
```

### Chat
```
POST   /api/chat/sessions              Create session (protected)
GET    /api/chat/sessions              List sessions (protected)
POST   /api/chat/query                 Send message (protected, streaming)
GET    /api/chat/history/{session_id}  Get chat history (protected)
DELETE /api/chat/sessions/{id}         Delete session (protected)
```

### Literature
```
GET    /api/literature/search          Search papers
POST   /api/literature/sync            Sync latest papers (admin)
GET    /api/literature/{pmid}          Get paper detail
GET    /api/literature/topic/{topic}   Papers by topic
```

### Images
```
POST   /api/images/analyze             Upload and analyze X-ray (protected)
GET    /api/images/{id}                Get analysis result (protected)
POST   /api/images/{id}/findings       Add findings (protected)
```

### Timeline
```
POST   /api/timeline                   Create timeline (protected)
GET    /api/timeline/{id}              Get timeline (protected)
GET    /api/timeline/{id}/events       Get events (protected)
POST   /api/timeline/{id}/summarize    Generate summary (protected)
```

### Dashboard
```
GET    /api/dashboard/stats            Statistics (protected)
GET    /api/dashboard/usage            Usage metrics (protected)
GET    /api/dashboard/eval-metrics     RAGAS metrics (protected)
```

---

## 🔧 SETUP COMMANDS

### Local Development Setup

```bash
# 1. Clone and enter directory
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start services with Docker
docker-compose up -d

# 5. Initialize database
python backend/scripts/init_db.py

# 6. Initialize Qdrant collections
python backend/scripts/init_qdrant.py

# 7. Start backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 8. In new terminal, start frontend
cd frontend
npm install
npm run dev
# Frontend at http://localhost:3000

# 9. Start Ollama (in another terminal)
ollama serve
# Then pull model:
ollama pull llama2:7b  # or llama3:8b
```

### Docker Compose Services
- **PostgreSQL:** localhost:5432
- **Qdrant:** localhost:6333
- **Ollama:** localhost:11434
- **Backend API:** localhost:8000
- **Frontend:** localhost:3000

---

## 📦 DEPENDENCIES

### Python (backend/requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.4.2
pydantic-settings==2.0.3
python-jwt==1.3.1
bcrypt==4.1.1
python-multipart==0.0.6
requests==2.31.0
httpx==0.25.1
langchain==0.1.1
langchain-community==0.0.4
qdrant-client==2.7.1
sentence-transformers==2.2.2
ollama==0.0.11
torch==2.1.1
torchvision==0.16.1
pillow==10.1.0
pdf2image==1.16.3
pytesseract==0.3.10
numpy==1.26.2
pandas==2.1.3
pytest==7.4.3
pytest-asyncio==0.21.1
```

### Node (frontend/package.json)
```json
{
  "dependencies": {
    "next": "15.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.3.6",
    "@shadcn/ui": "*",
    "axios": "^1.6.2",
    "zustand": "^4.4.1",
    "react-query": "^3.39.3"
  }
}
```

---

## 📋 NEXT IMMEDIATE STEPS

### Week 1 Priority:
1. [ ] Fix data setup script
2. [ ] Create Docker Compose configuration
3. [ ] Set up PostgreSQL + Qdrant
4. [ ] Create FastAPI scaffold
5. [ ] Create Next.js scaffold
6. [ ] Database schema initialization
7. [ ] Environment configuration

**Estimated Time:** 3-4 days

---

## 📚 RELATED DOCUMENTS

- **QUICK_START.md** - Fast setup guide
- **ACTION_PLAN.md** - Previous MVP plan
- **IMPLEMENTATION_SUMMARY.md** - Previous dataset implementation
- **DEVELOPMENT_GUIDE.md** - Original phases

---

**Start with:** Setting up Docker and creating full project structure
