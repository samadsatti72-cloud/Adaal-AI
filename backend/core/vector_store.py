# backend/core/vector_store.py
"""
AdaalAI — Vector Store
Uses TF-IDF + cosine similarity for offline, zero-download semantic search.
Works fully offline — no HuggingFace download required.

When deployed on a real server with internet access, swap _get_embedder() to
use SentenceTransformer('intfloat/multilingual-e5-large') for full multilingual
Urdu + English support. The rest of the API stays identical.
"""
from __future__ import annotations

import json
import os
import pickle
from typing import List, Dict, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.core.config import settings

# ── Paths for persisted index ──────────────────────────────────────────────────
_INDEX_DIR      = os.path.join(settings.BASE_DIR, "data", "tfidf_index")
_VECTORIZER_PKL = os.path.join(_INDEX_DIR, "vectorizer.pkl")
_MATRIX_NPY     = os.path.join(_INDEX_DIR, "matrix.npy")
_DOCS_PKL       = os.path.join(_INDEX_DIR, "docs.pkl")

# ── Module-level cache (loaded once per process) ───────────────────────────────
_vectorizer : TfidfVectorizer | None = None
_matrix     : np.ndarray      | None = None
_docs       : List[Dict]       | None = None   # list of {id, court, case_no, year, section, outcome, parties, text}


def _load_index() -> bool:
    """Load persisted index into module globals. Returns True if successful."""
    global _vectorizer, _matrix, _docs
    if not (os.path.exists(_VECTORIZER_PKL) and
            os.path.exists(_MATRIX_NPY)     and
            os.path.exists(_DOCS_PKL)):
        return False
    with open(_VECTORIZER_PKL, "rb") as f:
        _vectorizer = pickle.load(f)
    _matrix = np.load(_MATRIX_NPY)
    with open(_DOCS_PKL, "rb") as f:
        _docs = pickle.load(f)
    return True


def build_index(judgments_path: str | None = None) -> int:
    """
    Build a TF-IDF index from judgments JSON and persist it to disk.
    Safe to call multiple times — rebuilds from scratch each time.

    Returns:
        Number of documents indexed.
    """
    global _vectorizer, _matrix, _docs

    path = judgments_path or settings.JUDGMENTS_PATH
    with open(path, "r", encoding="utf-8") as f:
        judgments: List[Dict] = json.load(f)

    os.makedirs(_INDEX_DIR, exist_ok=True)

    # Build rich text representation for each judgment
    docs_meta = []
    corpus    = []
    for j in judgments:
        full_text = (
            f"Court {j['court']} "
            f"Case {j['case_no']} "
            f"Year {j['year']} "
            f"Parties {j['parties']} "
            f"Section {j['section']} PPC "
            f"Outcome {j['outcome']} "
            f"Summary {j['summary']} "
            f"Legal principle {j.get('legal_principle', '')} "
            f"Keywords {' '.join(j.get('keywords', []))}"
        )
        corpus.append(full_text)
        docs_meta.append({
            "id"      : j["id"],
            "court"   : j["court"],
            "case_no" : j["case_no"],
            "year"    : j["year"],
            "section" : j["section"],
            "outcome" : j["outcome"],
            "parties" : j["parties"],
            "text"    : full_text,
        })

    # Fit TF-IDF (unigrams + bigrams, English + Urdu words handled as tokens)
    vec = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
        analyzer="word",
    )
    mat = vec.fit_transform(corpus)

    # Persist
    with open(_VECTORIZER_PKL, "wb") as f:
        pickle.dump(vec, f)
    np.save(_MATRIX_NPY, mat.toarray())
    with open(_DOCS_PKL, "wb") as f:
        pickle.dump(docs_meta, f)

    # Update globals
    _vectorizer = vec
    _matrix     = mat.toarray()
    _docs       = docs_meta

    print(f"[VectorStore] TF-IDF index built — {len(docs_meta)} documents ✓")
    return len(docs_meta)


def search_judgments(
    query: str,
    top_k: int = 5,
    section_filter: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Search Pakistani court judgments by TF-IDF cosine similarity.

    Args:
        query:          Natural-language query (Urdu or English).
        top_k:          Number of results to return.
        section_filter: Optional PPC section to restrict results (e.g. "302").

    Returns:
        List of dicts: id, court, case_no, year, section, outcome, parties,
                       text, distance (1 - similarity).
    """
    global _vectorizer, _matrix, _docs

    # Lazy-load persisted index if not in memory
    if _vectorizer is None:
        if not _load_index():
            return []

    q_vec = _vectorizer.transform([query]).toarray()
    sims  = cosine_similarity(q_vec, _matrix)[0]

    # Rank all docs by similarity
    ranked_idx = np.argsort(sims)[::-1]

    results = []
    for idx in ranked_idx:
        doc = _docs[idx]
        # Optional section filter
        if section_filter and doc["section"] != section_filter:
            continue
        results.append({
            **doc,
            "distance": round(float(1 - sims[idx]), 4),
        })
        if len(results) >= top_k:
            break

    return results


def collection_size() -> int:
    """Return how many documents are currently indexed."""
    global _docs
    if _docs is None:
        _load_index()
    return len(_docs) if _docs else 0
