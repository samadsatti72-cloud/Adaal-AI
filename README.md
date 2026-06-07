# AdaalAI — AI-Powered Judicial Assistance for Pakistan

**Free · Open Source · Urdu-First · Citizen-Facing**

AdaalAI applies AI and ML to reduce Pakistan's **2.2 million case backlog** and make legal
help accessible to every citizen — not just those who can afford a lawyer.

---

## Modules

| # | Module | Tech | Status |
|---|--------|------|--------|
| 1 | **Legal Research Assistant** | TF-IDF RAG + LLM (Groq/Llama 3) | ✅ Working |
| 2 | **FIR Auto-Draft (Urdu + English)** | NLP keyword matching + LLM | ✅ Working |
| 3 | **Case Prioritization Engine** | XGBoost ML classifier | ✅ Working (97.5% accuracy) |
| 4 | **Citizen Rights Chatbot (Urdu)** | LLM + legal knowledge base | ✅ Working |

---

## Project Structure

```
adaalai/
├── backend/
│   ├── api/
│   │   └── main.py           ← FastAPI app — all API routes
│   ├── core/
│   │   ├── config.py         ← Central settings from .env
│   │   ├── llm_client.py     ← Groq/OpenAI client + offline demo mode
│   │   └── vector_store.py   ← TF-IDF index for judgment search
│   └── models/
│       ├── legal_research.py ← Module 1: RAG legal research
│       ├── fir_drafting.py   ← Module 2: FIR auto-draft
│       ├── case_priority.py  ← Module 3: XGBoost case scoring
│       └── citizen_chatbot.py← Module 4: Citizen rights chatbot
├── data/                     ← Generated on setup (git-ignored)
│   ├── ppc_sections.json     ← 14 PPC sections with Urdu descriptions
│   ├── judgments.json        ← 8 sample SC/LHC/PHC/SHC judgments
│   ├── cases.json            ← 200 synthetic training cases (for XGBoost)
│   ├── tfidf_index/          ← Persisted TF-IDF vector index
│   └── priority_model.json   ← Trained XGBoost model
├── frontend/
│   └── index.html            ← Complete React UI (single file, no build)
├── scripts/
│   ├── seed_data.py          ← Generates all training/demo data
│   └── setup.py              ← One-command first-time setup
├── .env.example              ← Copy to .env and add your API key
└── requirements.txt
```

---

## Local Deployment — Step by Step

### Prerequisites

- Python 3.10 or higher
- pip
- A free [Groq API key](https://console.groq.com) *(optional — works in demo mode without it)*

---

### Step 1 — Clone / Download the project

```bash
# If using git:
git clone https://github.com/yourusername/adaalai.git
cd adaalai

# Or just unzip the downloaded folder and cd into it
cd adaalai
```

---

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs: FastAPI, uvicorn, scikit-learn, XGBoost, LangChain, openai, pandas, numpy, chromadb, and other dependencies. No GPU required.

---

### Step 3 — Configure environment

```bash
cp .env.example .env
```

Open `.env` in any text editor and set your Groq API key:

```
GROQ_API_KEY=gsk_your_key_here
```

**How to get a free Groq API key:**
1. Go to https://console.groq.com
2. Sign up (free — no credit card needed)
3. Click "API Keys" → "Create API Key"
4. Copy the key into your `.env` file

> **Without a key:** The system runs in **demo mode** — all 4 modules work with rich
> pre-written responses so you can test the full UI and API. Add the key when ready
> for real AI responses.

---

### Step 4 — Run first-time setup

```bash
python scripts/setup.py
```

This will:
- Generate the legal corpus (PPC sections, judgments, case data)
- Build the TF-IDF vector index for judgment search
- Train the XGBoost case prioritization model (200 training cases, ~97% accuracy)

Expected output:
```
══════════════════════════════════════════════════════
  AdaalAI — Setup
══════════════════════════════════════════════════════
────────────────────────────────────────────────────────
  Step 1/3: Generating legal corpus data...
────────────────────────────────────────────────────────
✅  Seeded 14 PPC sections → data/ppc_sections.json
✅  Seeded 8 judgments       → data/judgments.json
✅  Seeded 200 case records  → data/cases.json
────────────────────────────────────────────────────────
  Step 2/3: Building TF-IDF judgment vector index...
────────────────────────────────────────────────────────
[VectorStore] TF-IDF index built — 8 documents ✓
────────────────────────────────────────────────────────
  Step 3/3: Training XGBoost case prioritization model...
────────────────────────────────────────────────────────
[CasePriority] Model trained — accuracy: 97.50%
✅  Setup Complete!
```

---

### Step 5 — Start the backend server

```bash
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

### Step 6 — Open the frontend

Open `frontend/index.html` directly in your browser:

```
# On Windows:
start frontend/index.html

# On Mac:
open frontend/index.html

# On Linux:
xdg-open frontend/index.html
```

Or just drag `frontend/index.html` into Chrome/Firefox.

> The frontend talks to `http://localhost:8000` by default. Make sure your backend is running.

---

### Step 7 — Explore the API docs

FastAPI auto-generates interactive docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## API Reference

### Health Check
```
GET /
```

### Module 1 — Legal Research
```
POST /api/research
{
  "query": "bail rights murder case Section 302",
  "top_k": 5,
  "section_filter": "302"   // optional
}
```

### Module 2 — FIR Auto-Draft
```
POST /api/fir/draft
{
  "complaint_text": "Someone broke into my house and stole my mobile phone and cash"
}
```

### Module 3 — Score a Single Case
```
POST /api/cases/score
{
  "case_id": "LHC-2024-001",
  "charge_section": "302",
  "charge_severity": 3,
  "days_pending": 450,
  "adjournments": 14,
  "is_under_trial": 1,
  "under_trial_days": 450,
  "court_visits": 10,
  "accused_age": 28,
  "status": "Under Trial"
}
```

### Module 3 — Rank a Judge's Docket
```
POST /api/cases/docket
{
  "cases": [ { ...case objects... } ]
}
```

### Module 4 — Citizen Chatbot
```
POST /api/chat
{
  "question": "میری گرفتاری کے وقت میرے کیا حقوق ہیں؟"
}
```

### Admin — Build Index
```
POST /api/admin/build-index
```

### Admin — Train Model
```
POST /api/admin/train-model
```

### Admin — System Status
```
GET /api/admin/status
```

---

## Upgrading to Full Multilingual Embeddings (Production)

The default setup uses TF-IDF for offline, zero-download operation.
For production with full Urdu + English semantic search:

1. Install: `pip install sentence-transformers`
2. In `backend/core/vector_store.py`, replace the TF-IDF block with:
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('intfloat/multilingual-e5-large')
   ```
3. Re-run `python scripts/setup.py` to rebuild the index
4. The model downloads ~1.1 GB on first run — works in Urdu, English, and 100+ languages

---

## Tech Stack (100% Free)

| Component | Tool |
|-----------|------|
| Web Framework | FastAPI + Uvicorn |
| Retrieval (Search) | TF-IDF / scikit-learn (offline) → multilingual-e5-large (production) |
| ML Model | XGBoost (case prioritization) |
| LLM (AI text generation) | Groq API — Llama 3 8B (free tier) |
| Vector Storage | pickle + numpy (offline) → pgvector (production) |
| NLP | scikit-learn + keyword matching |
| Frontend | React 18 (CDN, no build step) |
| Database | JSON files (dev) → PostgreSQL (production) |
| Hosting | Any machine with Python — Oracle Cloud Free Tier recommended |

---

## Adding More Judgments

Edit `scripts/seed_data.py` and add entries to the `JUDGMENTS` list:

```python
{
    "id": "SC-2024-001",
    "court": "Supreme Court of Pakistan",
    "case_no": "Criminal Appeal No. 1 of 2024",
    "year": 2024,
    "parties": "ABC vs. State",
    "section": "302",
    "outcome": "Acquittal",
    "summary": "Full case summary here...",
    "keywords": ["murder", "302", "acquittal", "benefit of doubt"],
    "judges": ["Justice X"],
    "legal_principle": "Key legal principle established..."
}
```

Then rebuild the index:
```bash
curl -X POST http://localhost:8000/api/admin/build-index
```

---

## Compliance

AdaalAI is designed in compliance with the **NJPMC AI Guidelines (April 29, 2026)**:
- ✅ Human-in-the-loop: all AI outputs require human approval before any action
- ✅ Explainability: every answer cites the source judgment
- ✅ Advisory only: AI never makes judicial decisions
- ✅ Audit trail: all API calls are logged

---

## License

MIT License — free to use, modify, and deploy. Built for Pakistan's 220 million people.

---

*AdaalAI — Because justice should not depend on who you know or what you can afford.*
