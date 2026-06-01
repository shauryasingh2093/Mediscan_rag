# ACTION PLAN FOR YOU

## 📋 Complete Setup Tasks

This document outlines everything you need to do to get MediScan RAG Phase 1 MVP running.

---

## WEEK 1: Data Setup & Integration

### Step 1: Install New Dependencies
**Time: 5 minutes**

Run:
```bash
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag
pip install -r requirements.txt
```

This installs:
- numpy (for MedMNIST image handling)
- Existing dependencies (FastAPI, ChromaDB, etc.)

### Step 2: Download & Prepare Datasets
**Time: 10-15 minutes**

Run the complete Phase 1 setup:
```bash
python -m backend.scripts.setup_datasets --phase 1
```

What this does:
1. ✅ Downloads ChestMNIST dataset (~50 MB)
2. ✅ Creates subset of 1,000 samples (faster training)
3. ✅ Fetches/generates 500 PubMed abstracts
4. ✅ Registers all datasets in manager
5. ✅ Creates `data/datasets_metadata.json` catalog

**Expected outputs:**
```
data/
├── medmnist/
│   └── chestmnist_subset_1000.npz
├── pubmed/
│   └── abstracts.jsonl
└── datasets_metadata.json
```

### Step 3: Verify Dataset Registration
**Time: 2 minutes**

Check that datasets are registered:
```bash
python -c "
from backend.datasets.manager import DatasetManager
manager = DatasetManager('./data')
print('Registered datasets:')
for ds in manager.list_datasets():
    print(f'  - {ds[\"name\"]} v{ds[\"version\"]}: {ds[\"num_samples\"]} samples')
print()
print(manager.get_summary())
"
```

---

## WEEK 2: RAG Pipeline Integration

### Step 4: Create Data Ingestion Endpoint
**Time: 30-45 minutes**

Create `backend/app/api/datasets.py`:
```python
from fastapi import APIRouter, Query
from backend.datasets.manager import DatasetManager
from backend.datasets.preprocessor import DataPreprocessor

router = APIRouter()

@router.get("/datasets")
def list_datasets():
    """List all registered datasets."""
    manager = DatasetManager('./data')
    return {
        "datasets": manager.list_datasets(),
        "summary": manager.get_summary(),
    }

@router.post("/datasets/ingest/{dataset_name}")
def ingest_dataset(dataset_name: str, version: str = "latest"):
    """Ingest a dataset into ChromaDB."""
    manager = DatasetManager('./data')
    dataset_path = manager.get_dataset_path(dataset_name, version)
    
    if not dataset_path:
        return {"error": f"Dataset not found: {dataset_name}"}
    
    # TODO: Load dataset and insert into ChromaDB
    # Use existing ingestion API
    
    return {"status": "ingestion started", "dataset": dataset_name}
```

Add to `backend/app/main.py`:
```python
from .api.datasets import router as datasets_router
app.include_router(datasets_router, prefix="/api")
```

### Step 5: Load Datasets into ChromaDB
**Time: 45-60 minutes**

Update `backend/app/api/ingestion.py` to support:

1. **MedMNIST images:**
   - Convert images to JPEG/base64
   - Create text descriptions from labels
   - Embed and store in ChromaDB

2. **PubMed abstracts:**
   - Load from JSONL
   - Create RAG documents
   - Chunk + embed + store

Example:
```python
from backend.datasets.medmnist_loader import MedMNISTLoader
from backend.datasets.pubmed_crawler import PubMedCrawler
from backend.vector_db.store import ChromaStore

async def ingest_medmnist():
    loader = MedMNISTLoader('./data/medmnist')
    images, labels = loader.load_dataset('chestmnist')
    
    # Convert to documents
    documents = []
    for i, (img, label) in enumerate(zip(images, labels)):
        doc = {
            "id": f"medmnist_{i}",
            "title": f"Chest X-ray {i}",
            "content": f"Chest X-ray image. Classification: {label}",
            "metadata": {"source": "medmnist", "label": int(label)},
        }
        documents.append(doc)
    
    # Store in ChromaDB
    store = ChromaStore()
    store.add_documents(documents)
    
    return {"ingested": len(documents)}
```

### Step 6: Test Retrieval
**Time: 20-30 minutes**

Test that you can:
1. ✅ Upload a query
2. ✅ Get relevant documents back from both MedMNIST and PubMed
3. ✅ Display results with citations

Example test:
```bash
# Test retrieval
curl -X POST "http://127.0.0.1:8000/api/datasets/ingest/medmnist"
curl -X POST "http://127.0.0.1:8000/api/datasets/ingest/pubmed"

# Query
curl -X POST "http://127.0.0.1:8000/api/retrieval/search" \
  -d "query=chest+x-ray+findings"
```

---

## WEEK 3: MVP UI & Demo

### Step 7: Create Upload Interface
**Time: 1-2 hours**

Build simple web UI for:
- Upload X-ray image or medical report
- See extracted text
- View similar documents from RAG
- Chat interface

### Step 8: Demo Preparation
**Time: 1 hour**

Create demo script that shows:
1. Data strategy (this doc)
2. Dataset management (list, info, stats)
3. Multimodal RAG in action
4. Real search results

---

## WEEK 4: Prepare for MIMIC-CXR Phase 2

### Step 9: Apply for PhysioNet Access
**Time: 5 minutes setup + 3-5 days approval**

1. Go to: https://physionet.org/register/
2. Create free account
3. Find MIMIC-CXR-JPG v2.1.0
4. Sign data use agreement
5. Complete CITI training (online course, ~1 hour)

### Step 10: Prepare MIMIC Setup Script
**Time: Already done! ✅**

When PhysioNet approves, just run:
```bash
python -m backend.scripts.setup_mimic_subset \
  --num_studies 1000 \
  --output_dir ./data/mimic_cxr_subset
```

---

## WHAT YOU NEED TO DO RIGHT NOW

### Immediate Actions (Today)

1. **Install dependencies:**
   ```bash
   pip install numpy
   ```

2. **Run Phase 1 setup:**
   ```bash
   python -m backend.scripts.setup_datasets --phase 1
   ```

3. **Verify data was downloaded:**
   ```bash
   ls -la data/
   ```

### This Week

4. **Create dataset ingestion endpoint** (`backend/app/api/datasets.py`)

5. **Integrate with ChromaDB** (update ingestion API)

6. **Test retrieval** (make sure documents are searchable)

### Next Steps

7. **Build UI** (upload + search interface)

8. **Create demo** (show complete workflow)

9. **Apply for MIMIC** (takes time to approve)

---

## WHAT EACH SCRIPT DOES

### `setup_datasets.py` (Master Script)
**Main entry point for all dataset operations**

```bash
# Show full plan and instructions
python -m backend.scripts.setup_datasets --phase 0

# Setup Phase 1 MVP (MedMNIST + PubMed)
python -m backend.scripts.setup_datasets --phase 1

# Setup Phase 2 (MIMIC-CXR) - after PhysioNet approval
python -m backend.scripts.setup_datasets --phase 2
```

### `download_medmnist.py` (MedMNIST Loader)
**Download specific MedMNIST dataset**

```bash
# Download ChestMNIST
python -m backend.scripts.download_medmnist --dataset chestmnist

# Download and create subset
python -m backend.scripts.download_medmnist \
  --dataset chestmnist \
  --subset 1000

# Force re-download
python -m backend.scripts.download_medmnist \
  --dataset chestmnist \
  --force
```

### `fetch_pubmed.py` (PubMed Crawler)
**Fetch medical research abstracts**

```bash
# Fetch all topics (500 papers each)
python -m backend.scripts.fetch_pubmed --num-papers 500

# Fetch specific topic
python -m backend.scripts.fetch_pubmed \
  --topic pneumonia \
  --num-papers 100
```

---

## DATASET MODULE BREAKDOWN

### `backend/datasets/manager.py`
- Centralized dataset management
- Tracks versions, sizes, metadata
- Validates dataset existence
- Provides summary statistics

### `backend/datasets/medmnist_loader.py`
- Download MedMNIST datasets
- Load into numpy arrays
- Create subsets for quick testing
- Convert to RAG-compatible format

### `backend/datasets/pubmed_crawler.py`
- Fetch PubMed abstracts
- Search by topic
- Save in JSONL format
- Convert to RAG documents

### `backend/datasets/mimic_handler.py`
- Handle MIMIC-CXR multimodal data
- Register studies
- Compare reports over time
- Create RAG documents from findings

### `backend/datasets/preprocessor.py`
- Chunk text for embeddings
- Extract medical entities
- Clean medical text
- Validate RAG documents

---

## EXPECTED TIMELINE

| Week | Task | Status |
|------|------|--------|
| 1 | Download datasets, verify setup | ✅ Ready to start |
| 2 | Integrate with RAG pipeline | Next |
| 3 | Build UI and demo | Following |
| 4+ | MIMIC phase 2 (waiting for approval) | Future |

---

## TROUBLESHOOTING

### "Dataset not found" error
```bash
# Verify datasets were downloaded
ls -la data/medmnist/
ls -la data/pubmed/

# Re-run setup
python -m backend.scripts.setup_datasets --phase 1 --force
```

### "Import errors" when running scripts
```bash
# Make sure you're in the right directory
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag

# Verify Python path
python -c "import sys; print(sys.path)"
```

### "Out of memory" on Mac
The MVP datasets are tiny (~50 MB), so this shouldn't happen. If it does:
```bash
# Use even smaller subset
python -m backend.scripts.download_medmnist \
  --subset 100
```

---

## SUCCESS CRITERIA

You'll know Phase 1 is complete when:

✅ Datasets are downloaded and registered  
✅ MedMNIST images are in ChromaDB  
✅ PubMed abstracts are searchable  
✅ API returns relevant results for searches  
✅ Frontend shows retrieved documents with citations  
✅ Can compare with interview-level projects  

---

## NEXT CONVERSATION STARTERS

Once Phase 1 is done, ask me:
- "How do I integrate these datasets with the RAG pipeline?"
- "How do I build the frontend for upload + search?"
- "How do I evaluate retrieval quality?"
- "How do I prepare the demo?"

---

**Good luck! This is a really solid approach to building a production-level medical AI project. 🚀**
