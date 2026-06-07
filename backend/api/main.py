# backend/api/main.py
"""
AdaalAI — FastAPI Application
All four modules exposed as REST API endpoints.

Endpoints:
  GET  /                          Health check + system status
  POST /api/research              Module 1: Legal research (RAG)
  POST /api/fir/draft             Module 2: FIR auto-draft
  POST /api/cases/score           Module 3: Score a single case
  POST /api/cases/docket          Module 3: Score + rank a docket
  POST /api/chat                  Module 4: Citizen chatbot
  POST /api/admin/build-index     Admin: build/rebuild judgment vector index
  POST /api/admin/train-model     Admin: train/retrain XGBoost model
  GET  /api/admin/status          Admin: system status
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core import vector_store
from backend.models import legal_research, fir_drafting, case_priority, citizen_chatbot

# ── App init ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered judicial assistance for Pakistan. "
        "Legal research, FIR drafting, case prioritization, citizen guidance."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response schemas ─────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query:          str            = Field(..., min_length=5, description="Legal question (English or Urdu)")
    top_k:          int            = Field(5, ge=1, le=10, description="Number of judgments to retrieve")
    section_filter: Optional[str]  = Field(None, description="Filter by PPC section e.g. '302'")

class FIRRequest(BaseModel):
    complaint_text: str = Field(..., min_length=20, description="Complainant's statement (Urdu or English)")

class CaseModel(BaseModel):
    case_id:          str   = Field("", description="Unique case identifier")
    charge_section:   str   = Field("", description="PPC section e.g. '302'")
    charge_severity:  int   = Field(1, ge=1, le=3, description="1=Low 2=Medium 3=High")
    days_pending:     int   = Field(0, ge=0, description="Days since case was registered")
    adjournments:     int   = Field(0, ge=0, description="Number of adjournments so far")
    is_under_trial:   int   = Field(0, ge=0, le=1, description="1 if accused is in custody")
    under_trial_days: int   = Field(0, ge=0, description="Days accused has been in custody")
    court_visits:     int   = Field(1, ge=1, description="Total hearings held so far")
    accused_age:      int   = Field(30, ge=10, le=120, description="Age of the accused")
    status:           str   = Field("", description="Current case status")

class DocketRequest(BaseModel):
    cases: List[CaseModel] = Field(..., min_length=1, description="List of cases to score and rank")

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Legal question in Urdu or English")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "app"    : settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status" : "running",
        "docs"   : "/docs",
        "modules": ["legal_research", "fir_draft", "case_priority", "citizen_chat"],
    }


# ── Module 1: Legal Research ───────────────────────────────────────────────────
@app.post("/api/research")
async def research_endpoint(req: ResearchRequest):
    """
    Semantic search + LLM answer over Pakistani court judgments.
    Returns grounded answer with case citations.
    """
    if vector_store.collection_size() == 0:
        raise HTTPException(
            status_code=503,
            detail=(
                "Judgment index is empty. "
                "Call POST /api/admin/build-index first to build the vector index."
            ),
        )
    result = legal_research.research(
        query=req.query,
        top_k=req.top_k,
        section_filter=req.section_filter,
    )
    return result


# ── Module 2: FIR Drafting ────────────────────────────────────────────────────
@app.post("/api/fir/draft")
async def fir_draft_endpoint(req: FIRRequest):
    """
    Generate a bilingual (English + Urdu) FIR draft from a complainant's statement.
    Matches relevant PPC sections via keyword NLP.
    Draft must be reviewed and approved by a police officer before filing.
    """
    result = fir_drafting.draft_fir(req.complaint_text)
    return result


# ── Module 3: Case Prioritization ─────────────────────────────────────────────
@app.post("/api/cases/score")
async def score_case_endpoint(case: CaseModel):
    """
    Score a single case's priority using the XGBoost model.
    Returns: priority (High/Medium/Low), confidence, and flags.
    """
    result = case_priority.score_case(case.model_dump())
    return result


@app.post("/api/cases/docket")
async def score_docket_endpoint(req: DocketRequest):
    """
    Score and rank a full list of cases (a judge's docket).
    Returns cases sorted High → Medium → Low with flags.
    """
    cases = [c.model_dump() for c in req.cases]
    ranked = case_priority.score_docket(cases)
    return {
        "total_cases": len(ranked),
        "high"       : sum(1 for c in ranked if c["priority_score"] == 2),
        "medium"     : sum(1 for c in ranked if c["priority_score"] == 1),
        "low"        : sum(1 for c in ranked if c["priority_score"] == 0),
        "docket"     : ranked,
    }


# ── Module 4: Citizen Chatbot ─────────────────────────────────────────────────
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Citizen-facing chatbot. Answers legal rights questions in Urdu + English.
    Provides emergency contacts when urgent situations are detected.
    """
    result = citizen_chatbot.answer(req.question)
    return result


# ── Admin Endpoints ───────────────────────────────────────────────────────────
@app.post("/api/admin/build-index")
async def build_index_endpoint(background_tasks: BackgroundTasks):
    """
    Build (or rebuild) the judgment vector index.
    Runs in background — check /api/admin/status for progress.
    """
    def _build():
        vector_store.build_index()
    background_tasks.add_task(_build)
    return {"message": "Index build started in background. Check /api/admin/status"}


@app.post("/api/admin/train-model")
async def train_model_endpoint(background_tasks: BackgroundTasks):
    """
    Train (or retrain) the XGBoost case prioritization model.
    Runs in background.
    """
    def _train():
        case_priority.train()
    background_tasks.add_task(_train)
    return {"message": "Model training started in background."}


@app.get("/api/admin/status")
async def admin_status():
    """
    System status: index size, model availability, config.
    """
    return {
        "judgment_index_size"  : vector_store.collection_size(),
        "priority_model_ready" : case_priority.is_model_trained(),
        "embedding_model"      : settings.EMBEDDING_MODEL,
        "llm_provider"         : settings.LLM_PROVIDER,
        "llm_model"            : settings.LLM_MODEL,
    }
