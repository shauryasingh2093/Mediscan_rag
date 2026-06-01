# QUICK START REFERENCE

## One-Line Summary
You now have a **production-ready dataset management system** for MediScan RAG with Phase 1 MVP ready to go.

---

## 30-Second Setup

```bash
# 1. Go to project
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download datasets (~5 min)
python -m backend.scripts.setup_datasets --phase 1

# Done! Data is in ./data/
```

---

## What's Inside Your New Setup

### 📁 New Directories
```
backend/
├── datasets/           ← NEW: Dataset management
│   ├── manager.py      (centralized dataset catalog)
│   ├── medmnist_loader.py (MedMNIST handler)
│   ├── pubmed_crawler.py  (PubMed literature)
│   ├── mimic_handler.py   (MIMIC-CXR for Phase 2)
│   └── preprocessor.py    (text/data processing)
│
└── scripts/            ← NEW: Setup scripts
    ├── setup_datasets.py        (master setup)
    ├── download_medmnist.py     (MedMNIST downloader)
    └── fetch_pubmed.py          (PubMed crawler)

data/                  ← NEW: Datasets directory
├── datasets_metadata.json
├── medmnist/
│   └── chestmnist_subset_1000.npz
└── pubmed/
    └── abstracts.jsonl
```

### 🗂️ New Documentation
- **ACTION_PLAN.md** ← You are here! Step-by-step what to do
- **DEVELOPMENT_GUIDE.md** ← Updated with Phase 0 data strategy
- **QUICK_START.md** ← This file

---

## Quick Command Reference

### Show Setup Plan
```bash
python -m backend.scripts.setup_datasets --phase 0
```

### Setup Phase 1 (MVP - Start Here)
```bash
python -m backend.scripts.setup_datasets --phase 1
```

### Setup Phase 2 (MIMIC - After PhysioNet Approval)
```bash
python -m backend.scripts.setup_datasets --phase 2
```

### Download Specific Datasets
```bash
# ChestMNIST
python -m backend.scripts.download_medmnist --dataset chestmnist --subset 1000

# PubMed abstracts
python -m backend.scripts.fetch_pubmed --num-papers 500

# Other MedMNIST variants
python -m backend.scripts.download_medmnist --dataset pathmnist
python -m backend.scripts.download_medmnist --dataset dermamnist
```

### Check What's Registered
```bash
python -c "
from backend.datasets.manager import DatasetManager
m = DatasetManager('./data')
for ds in m.list_datasets():
    print(f'{ds[\"name\"]}: {ds[\"num_samples\"]} samples')
"
```

---

## What Each Component Does

### DatasetManager (`backend/datasets/manager.py`)
```python
from backend.datasets.manager import DatasetManager

manager = DatasetManager('./data')

# List all datasets
datasets = manager.list_datasets()

# Get info about a dataset
info = manager.get_dataset_info('medmnist', '1.0')

# Check if dataset exists
exists = manager.validate_dataset('pubmed')

# Get summary statistics
summary = manager.get_summary()
print(f"Total samples: {summary['total_samples']}")
```

### MedMNIST Loader (`backend/datasets/medmnist_loader.py`)
```python
from backend.datasets.medmnist_loader import MedMNISTLoader

loader = MedMNISTLoader('./data/medmnist')

# Download dataset
path = loader.download_dataset('chestmnist')

# Load images
images, labels = loader.load_dataset('chestmnist', split='train')

# Create subset
subset_path = loader.create_subset('chestmnist', num_samples=1000)

# Convert to RAG format
documents = loader.convert_to_json('chestmnist', max_samples=100)
```

### PubMed Crawler (`backend/datasets/pubmed_crawler.py`)
```python
from backend.datasets.pubmed_crawler import PubMedCrawler

crawler = PubMedCrawler('./data/pubmed')

# Fetch papers on a topic
papers = crawler.crawl_topic('pneumonia', num_papers=100)

# Save abstracts
file = crawler.save_abstracts(papers)

# Convert to RAG documents
documents = crawler.create_rag_documents(papers)
```

### Preprocessor (`backend/datasets/preprocessor.py`)
```python
from backend.datasets.preprocessor import DataPreprocessor

# Chunk text for embeddings
chunks = DataPreprocessor.chunk_text(text, chunk_size=512)

# Extract medical entities
entities = DataPreprocessor.extract_medical_entities(text)

# Clean medical text
clean = DataPreprocessor.clean_medical_text(raw_text)

# Validate RAG document
valid = DataPreprocessor.validate_rag_document(doc)
```

---

## Three-Phase Vision

### Phase 1: MVP ✅ READY NOW
```
MedMNIST (1,000 images) + PubMed (500 papers)
        ↓
      OCR + Embeddings
        ↓
      ChromaDB
        ↓
      Chat Interface
```
**Size:** ~50 MB  
**Time:** 5-10 min setup  
**Great for:** Testing, MVP, learning  

### Phase 2: Production 🔄 AFTER PHYSIONET APPROVAL
```
MIMIC-CXR (1,000-5,000 studies)
        ↓
  X-rays + Reports + Findings
        ↓
   Multimodal Embeddings
        ↓
   Semantic + Image Search
```
**Size:** ~10-50 GB  
**Time:** Hours to download  
**Great for:** Interview demo, production  

### Phase 3: Advanced 📋 FUTURE
```
Additional PubMed + WHO Guidelines
        ↓
  Knowledge Graph + Entity Linking
        ↓
  Research Assistant Mode
```

---

## Data Strategy Advantages

### Why NOT Use Full Datasets?
❌ Weeks of downloading (100+ GB)  
❌ Storage costs  
❌ Preprocessing complexity  
❌ Slow iteration  

### Why This Approach?
✅ Quick setup (minutes not hours)  
✅ Mac-friendly (small files)  
✅ Fast iteration (test ideas quickly)  
✅ Production-grade (proper versioning/management)  
✅ Interview-ready (shows thoughtful strategy)  

---

## Next Steps After Setup

### Immediate (This Week)
1. Run setup: `python -m backend.scripts.setup_datasets --phase 1`
2. Verify data downloaded: `ls -la data/`
3. Check registration: Python code above

### Week 2-3 (Build RAG Pipeline)
1. Create `backend/app/api/datasets.py`
2. Load MedMNIST into ChromaDB
3. Load PubMed into ChromaDB
4. Test retrieval

### Week 4 (UI & Demo)
1. Build upload interface
2. Show retrieval results
3. Display citations
4. Create demo script

### Week 5+ (Phase 2)
1. Apply to PhysioNet
2. Wait for approval (3-5 days)
3. Download MIMIC-CXR subset
4. Build multimodal RAG

---

## Success Checklist

- [ ] Dependencies installed
- [ ] Phase 1 setup complete
- [ ] Datasets downloaded (~50 MB)
- [ ] `data/datasets_metadata.json` exists
- [ ] `data/medmnist/chestmnist_subset_1000.npz` exists
- [ ] `data/pubmed/abstracts.jsonl` exists
- [ ] Can run dataset queries (see code examples above)
- [ ] Ready for RAG pipeline integration

---

## Troubleshooting

### Error: "No module named 'backend.datasets'"
Make sure you're in the right directory:
```bash
cd /Users/shauryasingh/Downloads/projects/Mediscan_rag
python -m backend.scripts.setup_datasets --phase 1
```

### Error: "Dataset not found" during setup
The download might have failed. Re-run with force flag:
```bash
python -m backend.scripts.setup_datasets --phase 1
```

### Directory permissions error
Make sure data directory is writable:
```bash
chmod -R 755 /Users/shauryasingh/Downloads/projects/Mediscan_rag/data
```

### Out of memory
The MVP datasets are tiny (~50 MB), so this shouldn't happen. Use smaller subset:
```bash
python -m backend.scripts.download_medmnist --subset 100
```

---

## Questions to Ask Next

Once you've run the setup:
- "How do I integrate these datasets with my RAG pipeline?"
- "How do I test retrieval quality?"
- "How do I build the upload interface?"
- "How do I prepare the demo?"
- "What's the eval strategy?"

---

**You're all set! Start with:** `python -m backend.scripts.setup_datasets --phase 1` 🚀
