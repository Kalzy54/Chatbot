# MewarChat Settings Reference

## Overview
This document describes all configuration options in `config/settings.py` and how they affect functionality and performance.

---

## Settings for Maximum Functionality

The following configuration **maximizes functionality, accuracy, and retrieval quality**:

```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
CHUNK_SIZE_TOKENS = 900
CHUNK_OVERLAP_TOKENS = 300
SIMILARITY_THRESHOLD = 0.35
TOP_K = 8
```

### Why These Settings?

1. **Embedding Model: `all-mpnet-base-v2`**
   - Best semantic understanding for English and mixed-content documents
   - ~430MB download, excellent accuracy without extreme memory pressure
   - Superior to MiniLM (27M params vs 12M) for nuanced library queries
   - Alternatives:
     - `all-MiniLM-L12-v2`: Smaller (80MB), ~15% less accurate, use if memory-constrained
     - `all-mpnet-base-v2`: **BEST for balanced quality + performance**
     - `multilingual-e5-large`: Largest (~1.2GB), best multilingual, overkill for single-language library

2. **Chunk Size: 900 tokens**
   - ~3,600 characters per chunk (at 4 chars/token average)
   - Large enough to preserve paragraph context
   - Small enough to fit precise retrieval without noise
   - Increase to 1200 if documents are long-form articles; decrease to 600 if highly structured (tables, FAQs)

3. **Chunk Overlap: 300 tokens**
   - Ensures semantic continuity at chunk boundaries
   - Helps model understand connection between related content
   - Increased from default 200 for better context preservation

4. **Similarity Threshold: 0.35**
   - Confidence score filter (0.0 = no similarity, 1.0 = exact match)
   - 0.35 removes obvious non-matches while keeping relevantresults
   - Lower (0.15) = retrieve more, risk false positives
   - Higher (0.50) = strict filtering, may miss partial matches

5. **Top K: 8**
   - Retrieves top 8 most relevant chunks per query
   - Provides comprehensive context for LLM synthesis
   - Stays within token budget for GPT-4o-mini (128K context)
   - Increase to 10-15 for exhaustive answers; decrease to 3-5 for speed

---

## Environment Variables

All settings can be overridden via `.env` file. See `.env.example` for full reference.

```bash
OPENAI_API_KEY=sk-...                                           # Required
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2         # Recommended
CHUNK_SIZE_TOKENS=900                                          # Token count per chunk
CHUNK_OVERLAP_TOKENS=300                                       # Overlap between chunks
SIMILARITY_THRESHOLD=0.35                                      # Min relevance score
TOP_K=8                                                        # Num chunks to retrieve
UNIVERSITY_WEB_URL=                                            # Optional: website to crawl
```

---

## Tuning for Different Scenarios

### Scenario 1: Maximum Accuracy (Expert Research Queries)
```env
EMBEDDING_MODEL=sentence-transformers/multilingual-e5-large
CHUNK_SIZE_TOKENS=1200
CHUNK_OVERLAP_TOKENS=400
SIMILARITY_THRESHOLD=0.30
TOP_K=10
```
- **When to use:** PhD research, detailed policy documents, complex technical FAQs
- **Trade-off:** ~2-3x slower indexing, +2GB memory, slower inference
- **Result:** Highest accuracy, most comprehensive answers

### Scenario 2: Balanced (Recommended Default)
```env
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
CHUNK_SIZE_TOKENS=900
CHUNK_OVERLAP_TOKENS=300
SIMILARITY_THRESHOLD=0.35
TOP_K=8
```
- **When to use:** General library chat, mixed content, most use cases
- **Trade-off:** Good accuracy + reasonable speed
- **Result:** Best quality per resource spent

### Scenario 3: Resource-Constrained (Development on Low-Memory PC)
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L12-v2
CHUNK_SIZE_TOKENS=600
CHUNK_OVERLAP_TOKENS=150
SIMILARITY_THRESHOLD=0.40
TOP_K=5
SKIP_INGEST_ON_STARTUP=1
```
- **When to use:** Development on laptops, limited server RAM, quick prototyping
- **Trade-off:** ~15-20% lower accuracy, 3-5x faster indexing
- **Additional:** Set `SKIP_INGEST_ON_STARTUP=1` and run with `--workers 1` to minimize memory
- **Result:** Works on constrained systems, reasonable functionality

### Scenario 4: Real-Time Answers (Speed Priority)
```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L12-v2
CHUNK_SIZE_TOKENS=700
CHUNK_OVERLAP_TOKENS=200
SIMILARITY_THRESHOLD=0.45
TOP_K=3
```
- **When to use:** High-traffic production, sub-second response goals
- **Trade-off:** Lower accuracy, retrieves only highest-confidence results
- **Result:** Fast responses, moderate quality

---

## How Each Setting Affects Behavior

| Setting | Impact | Increase → | Decrease → |
|---------|--------|-----------|-----------|
| **EMBEDDING_MODEL size** | Accuracy | Better retrieval, slower, more memory | Faster but less nuanced |
| **CHUNK_SIZE_TOKENS** | Context | More context per result, less precision | Precise but fragmented |
| **CHUNK_OVERLAP_TOKENS** | Boundary coherence | Better transition semantics | Risk missing info at boundaries |
| **SIMILARITY_THRESHOLD** | Result filtering | Stricter relevance, risk missing valid answers | More noise, false positives |
| **TOP_K** | Answer comprehensiveness | More context, longer response time | Faster but less complete |

---

## Recommendation for Your Use Case

✅ **For Mewar University Library Chat:**
- Use the **Balanced** configuration (default in `settings.py`)
- Ingest full documents at startup (don't set `SKIP_INGEST_ON_STARTUP`)
- If PC struggles, switch to Resource-Constrained and deploy backend to a VM

If you need to maximize functionality **on your current PC**, you have two options:

1. **Use Balanced settings + deploy backend remotely** (best solution)
   - Run backend on cheap cloud VM ($5-15/month)
   - Run Streamlit locally pointing to remote API
   - Get maximum functionality without local resource pressure

2. **Use Resource-Constrained locally** with `SKIP_INGEST_ON_STARTUP=1`
   - Manually trigger ingestion via API when needed
   - Lower accuracy but works on limited hardware

---

## Modifying Settings

### Via `.env` file (recommended)
```bash
cp .env.example .env
# Edit .env with your values
```

### Via Python environment variables
```bash
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L12-v2"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Via PowerShell (Windows)
```powershell
$Env:EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
$Env:TOP_K = "8"
$Env:OPENAI_API_KEY = "sk-..."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## Advanced: Adding Custom Settings

To add new settings, edit `config/settings.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    CUSTOM_SETTING: str = os.getenv('CUSTOM_SETTING', 'default_value')
```

Then add to `.env`:
```env
CUSTOM_SETTING=my_value
```

Access in code:
```python
from config.settings import settings
print(settings.CUSTOM_SETTING)
```

---

## Performance Monitoring

Monitor these metrics to validate your settings:
- **Indexing time:** Time to build embeddings from documents (watch logs)
- **Query latency:** Time from question submission to answer return (< 5s ideal)
- **Memory usage:** Peak RAM during operation (Task Manager or `top`)
- **Hit rate:** % of questions with retrieved relevant context (audit chat logs)

---

## Questions?

Refer to `.env.example` for all available options with inline documentation.
