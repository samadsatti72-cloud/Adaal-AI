# backend/models/legal_research.py
"""
AdaalAI — Module 1: Legal Research Assistant
RAG pipeline: query → semantic retrieval → LLM answer with citations.

Every answer is grounded in retrieved documents.
If no relevant documents are found, the system says so — no hallucination.
"""
from __future__ import annotations

from typing import List, Dict, Any

from backend.core import vector_store
from backend.core.llm_client import chat

# ── System prompt (defines the AI's role) ─────────────────────────────────────
_SYSTEM_PROMPT = """You are AdaalAI, a legal research assistant specialising in Pakistani law.

Your role:
- Help lawyers and judges find relevant case law and legal principles
- Provide clear, accurate summaries of retrieved judgments
- Always cite the actual case source provided to you
- Write in clear, professional language (English, with Urdu terms where appropriate)

CRITICAL RULES:
1. Base your answer ONLY on the case documents provided below.
2. If the provided documents do not contain relevant information, say so clearly.
3. NEVER invent, guess, or fabricate case citations or legal principles.
4. Always state the court, case number, and year when citing a case.
5. End with a disclaimer: "This is AI-assisted legal research, not legal advice."
"""

_ANSWER_TEMPLATE = """
Based on the following retrieved Pakistani court judgments, answer the user's question.

RETRIEVED CASES:
{context}

USER QUESTION: {question}

Provide a structured answer with:
1. Direct answer to the question
2. Key legal principles from the cases
3. Relevant citations (court, case number, year)
4. Any important caveats or limitations

Remember: only use information from the retrieved cases above.
"""


def research(
    query: str,
    top_k: int = 5,
    section_filter: str | None = None,
) -> Dict[str, Any]:
    """
    Run a legal research query through the RAG pipeline.

    Args:
        query:          Natural-language legal question (English or Urdu).
        top_k:          Number of judgments to retrieve.
        section_filter: Optional PPC section to restrict search.

    Returns:
        {
            "answer":    str,            # LLM-generated answer grounded in sources
            "sources":   List[dict],     # retrieved judgment metadata
            "query":     str,
            "grounded":  bool,           # False if no relevant docs found
        }
    """
    # Step 1 — Retrieve semantically relevant judgments
    retrieved = vector_store.search_judgments(
        query=query,
        top_k=top_k,
        section_filter=section_filter,
    )

    if not retrieved:
        return {
            "answer"  : (
                "The judgment index is empty. Please run the index builder first, "
                "or no relevant cases were found for your query."
            ),
            "sources" : [],
            "query"   : query,
            "grounded": False,
        }

    # Step 2 — Build context block for LLM
    context_parts = []
    for i, doc in enumerate(retrieved, 1):
        context_parts.append(
            f"[{i}] CASE: {doc['case_no']} | COURT: {doc['court']} | "
            f"YEAR: {doc['year']} | SECTION: {doc['section']} PPC\n"
            f"OUTCOME: {doc['outcome']}\n"
            f"DETAILS: {doc['text'][:800]}\n"
        )
    context = "\n---\n".join(context_parts)

    # Step 3 — LLM generates grounded answer
    user_message = _ANSWER_TEMPLATE.format(
        context=context,
        question=query,
    )

    answer = chat(
        system_prompt=_SYSTEM_PROMPT,
        user_message=user_message,
    )

    return {
        "answer"  : answer,
        "sources" : [
            {
                "id"      : d["id"],
                "court"   : d["court"],
                "case_no" : d["case_no"],
                "year"    : d["year"],
                "section" : d["section"],
                "outcome" : d["outcome"],
                "parties" : d["parties"],
                "score"   : round(1 - d["distance"], 4),
            }
            for d in retrieved
        ],
        "query"   : query,
        "grounded": True,
    }
