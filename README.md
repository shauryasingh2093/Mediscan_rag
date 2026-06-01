# MediScan RAG - Production-Ready Multimodal Medical Intelligence Assistant

**Build an advanced AI-powered medical document intelligence and research platform.**

---

## 🎯 What is MediScan?

A comprehensive AI system that helps healthcare professionals:
- Upload and analyze medical reports (PDFs, text, DOCX)
- Search and understand medical research (PubMed integration)
- Analyze chest X-rays with AI (ResNet50 classifier)
- Ask questions and get citation-grounded answers (RAG with Llama 3)
- Track patient progression over time
- Evaluate AI quality metrics (RAGAS)

**This is NOT a diagnostic tool** - it's a medical knowledge and document intelligence platform.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MediScan RAG System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frontend (Next.js 15)                                          │
│  ├─ User Authentication                                         │
│  ├─ Document Upload UI                                          │
│  ├─ Chat Interface                                              │
│  ├─ Research Search                                             │
│  ├─ Image Analysis                                              │
│  └─ Patient Timeline                                            │
│                ↓ API ↓                                           │
│  Backend (FastAPI)                                              │
│  ├─ Auth Service (JWT)                                          │
│  ├─ Document Processing (OCR, PDF extraction)                   │
│  ├─ Embedding Service (BGE-small)                               │
│  ├─ RAG Engine (LangChain + Llama 3)                            │
│  ├─ PubMed Integration                                          │
│  └─ X-Ray Classifier (ResNet50)                                 │
│                ↓                                                 │
│  Data Layer                                                     │
│  ├─ PostgreSQL (documents, users, chat history)                │
│  ├─ Qdrant (vector embeddings)                                 │
│  ├─ Redis (caching, sessions)                                  │
│  └─ File Storage (uploads)                                     │
│                ↓                                                 │
│  AI Engine                                                      │
│  ├─ Ollama (Llama 3 8B)                                         │
│  ├─ Sentence Transformers (embeddings)                         │
│  └─ PyTorch (image classification)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Setup

```bash
# 1. Enter project directory
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start all services with Docker
docker-compose up -d

# 4. Verify services are running
docker-compose ps

# 5. Start backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 6. In new terminal, start frontend (when ready)
cd frontend
npm install
npm run dev
```

**Backend:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs  
**Frontend:** http://localhost:3000 (coming soon)

---

## 📋 12 Core Modules

1. **Authentication** - JWT, user management, protected routes
2. **Document Upload** - PDF/TXT processing, text extraction
3. **Text Processing** - Chunking, metadata, cleaning
4. **Embeddings** - BGE-small-en vector generation
5. **Vector Database** - Qdrant semantic search
6. **RAG Chat System** - LangChain, Llama 3, citations
7. **Medical Literature** - PubMed integration, auto-sync
8. **Chest X-Ray Analysis** - ResNet50 classifier, pneumonia detection
9. **Multimodal RAG** - Combined image + text understanding
10. **Patient Timeline** - Progression tracking, AI summaries
11. **Evaluation Dashboard** - RAGAS metrics, quality assurance
12. **Deployment** - Docker, production setup, monitoring

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Vector DB:** Qdrant
- **LLM:** Llama 3 (Ollama)
- **Embeddings:** BAAI/bge-small-en-v1.5
- **RAG:** LangChain
- **ML:** PyTorch, torchvision
- **Auth:** JWT (PyJWT, bcrypt)

### Frontend (Planned)
- **Framework:** Next.js 15
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI:** ShadCN UI
- **State:** Zustand, React Query

### Infrastructure
- **Containers:** Docker + Docker Compose
- **Caching:** Redis
- **File Storage:** Local filesystem (upgradeable to S3)

---

## 📂 Project Structure

```
mediscan-rag/
├── backend/
│   ├── app/
│   │   ├── api/              # Endpoint routers
│   │   ├── services/         # Business logic
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── database/         # DB connection
│   │   ├── core/             # Config, security
│   │   ├── utils/            # Utilities
│   │   └── main.py           # FastAPI app
│   ├── scripts/              # Setup & admin scripts
│   ├── ml_models/            # Trained models
│   ├── tests/                # Unit tests
│   └── Dockerfile            # Container config
│
├── frontend/
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   ├── services/             # API services
│   ├── types/                # TypeScript types
│   └── package.json
│
├── docker-compose.yml        # Service orchestration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── PROJECT_SPEC.md           # Architecture & API spec
├── BUILD_GUIDE.md            # Implementation guide
├── SETUP_COMPLETE.md         # What to do next
└── README.md                 # This file
```

---

## 📚 Documentation

- **[PROJECT_SPEC.md](./PROJECT_SPEC.md)** - Complete specifications, database schema, API endpoints
- **[BUILD_GUIDE.md](./BUILD_GUIDE.md)** - Phase-by-phase implementation with code examples
- **[SETUP_COMPLETE.md](./SETUP_COMPLETE.md)** - What to do right now
- **[API Docs](http://localhost:8000/docs)** - Interactive Swagger (when running)

---

## 🚀 Implementation Phases

### Phase 1: Foundation ✅
- Docker & services setup
- Database schema
- FastAPI skeleton
- Configuration

### Phase 2: Authentication
- Register/Login endpoints
- JWT tokens
- Protected routes

### Phase 3: Document Management
- PDF/TXT upload
- Text extraction (OCR)
- File storage

### Phase 4: RAG Chat
- Embeddings generation
- Vector search
- LLM integration
- Citation tracking

### Phase 5: PubMed Integration
- Literature search
- Auto-sync scheduler
- Document indexing

### Phase 6: X-Ray Analysis
- Model training
- Inference endpoint
- Result storage

### Phase 7-12: Advanced Features
- Multimodal RAG
- Patient timelines
- Evaluation metrics
- Production deployment

---

## 📊 Database Schema

### Core Tables
- **users** - User accounts and authentication
- **documents** - Uploaded medical documents
- **document_chunks** - Text chunks with embeddings
- **medical_literature** - PubMed papers
- **chat_sessions** - Conversation threads
- **messages** - Chat message history
- **image_findings** - X-ray analysis results
- **patient_timeline** - Patient progression events

See [PROJECT_SPEC.md](./PROJECT_SPEC.md) for complete schema.

---

## 🔧 API Endpoints

### Authentication
```
POST   /api/auth/register              Register new user
POST   /api/auth/login                 Login and get token
GET    /api/auth/profile               Get user profile (protected)
```

### Documents
```
POST   /api/documents                  Upload document
GET    /api/documents                  List documents
DELETE /api/documents/{id}             Delete document
```

### Chat
```
POST   /api/chat/sessions              Create chat session
POST   /api/chat/query                 Ask question (streaming)
GET    /api/chat/history/{session_id}  Get conversation history
```

### Literature
```
GET    /api/literature/search          Search papers
POST   /api/literature/sync            Sync latest papers
GET    /api/literature/{pmid}          Get paper details
```

### Images
```
POST   /api/images/analyze             Analyze X-ray
GET    /api/images/{id}                Get analysis result
```

### Timeline
```
GET    /api/timeline/{id}              Get patient timeline
POST   /api/timeline/{id}/summarize    Generate AI summary
```

---

## 🎯 Getting Started

### 1. Read the Documentation
- Start with [SETUP_COMPLETE.md](./SETUP_COMPLETE.md) (5 min)
- Then read [BUILD_GUIDE.md](./BUILD_GUIDE.md) (Phase 2)

### 2. Start Services
```bash
docker-compose up -d
uvicorn backend.app.main:app --reload
```

### 3. Follow Build Phases
Each phase in [BUILD_GUIDE.md](./BUILD_GUIDE.md) includes:
- Code examples
- Implementation steps
- Testing instructions

### 4. Implement Features
Focus on one phase at a time:
1. Authentication (4-6 hours)
2. Document upload (6-8 hours)
3. RAG chat (12-16 hours)
4. Advanced features

---

## 🧪 Testing

```bash
# Test backend is running
curl http://localhost:8000/health

# View API documentation
# Open http://localhost:8000/docs in browser

# Run test suite (when implemented)
pytest backend/tests/
```

---

## 🚢 Deployment

Complete deployment guide in [PROJECT_SPEC.md](./PROJECT_SPEC.md) Phase 12.

### Docker Production Build
```bash
docker build -t mediscan:latest .
docker run -p 8000:8000 mediscan:latest
```

### Environment Configuration
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
# Edit .env with production values
```

---

## 📈 Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| 1: Foundation | 2 days | ✅ Done |
| 2: Auth | 1 week | ⏳ Next |
| 3-4: Documents | 2 weeks | Coming |
| 5: RAG | 3 weeks | Coming |
| 6-7: Advanced | 3 weeks | Coming |
| 8-12: Polish | 2-4 weeks | Coming |
| **Total** | **12-16 weeks** | |

---

## 💡 Key Features Roadmap

- [x] Database schema
- [x] FastAPI setup
- [x] Docker orchestration
- [ ] User authentication
- [ ] Document upload & processing
- [ ] Embeddings & vector search
- [ ] RAG chat system
- [ ] PubMed integration
- [ ] X-ray classifier
- [ ] Patient timeline
- [ ] Evaluation dashboard
- [ ] Frontend (Next.js)
- [ ] Deployment

---

## 🤝 Contributing

This is a personal project for building a resume-worthy medical AI system.

---

## 📝 Resume Description

**MediScan RAG - Production-Ready Multimodal Medical Intelligence Assistant**

Built a comprehensive AI-powered platform combining FastAPI, Next.js, PostgreSQL, Qdrant, and Llama 3 to provide:
- Medical document analysis (OCR, text extraction)
- Semantic search over medical literature (PubMed integration)
- Citation-grounded question answering (RAG with LangChain)
- Medical image analysis (Chest X-rays, ResNet50 transfer learning)
- Patient timeline generation with AI summaries
- Quality metrics using RAGAS evaluation framework
- Production deployment with Docker and comprehensive monitoring

---

## 📞 Support & Questions

For questions about implementation:
1. Check [BUILD_GUIDE.md](./BUILD_GUIDE.md) for your specific phase
2. Review [PROJECT_SPEC.md](./PROJECT_SPEC.md) for architecture
3. Refer to inline code comments
4. Check API docs at `/docs` endpoint

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 🚀 Ready to Build?

**Start here:**
```bash
docker-compose up -d
uvicorn backend.app.main:app --reload
```

Then read [BUILD_GUIDE.md](./BUILD_GUIDE.md) → **Phase 2: Authentication**

**Let's build something amazing!** ✨
