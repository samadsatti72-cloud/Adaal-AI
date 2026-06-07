# backend/models/fir_drafting.py
"""
AdaalAI — Module 2: FIR Auto-Draft System
Pipeline:
  1. NLP keyword matching → identify relevant PPC sections
  2. LLM generates a bilingual (English + Urdu) FIR draft
  3. Returns draft + matched sections for officer review

Human-in-the-loop: the draft is for officer review only — no auto-filing.
"""
from __future__ import annotations

import json
import re
from typing import List, Dict, Any

from backend.core.config import settings
from backend.core.llm_client import chat


def _load_ppc() -> List[Dict]:
    """Load PPC sections from the local JSON data file."""
    with open(settings.PPC_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _match_sections(complaint_text: str) -> List[Dict]:
    """
    Keyword-based NLP matching to find relevant PPC sections.

    Strategy:
      - Lowercase the complaint text
      - For each PPC section keyword, check if it (or its stem) appears
        as a substring anywhere in the text
      - Also split text into words and check word-starts for partial matching
      - Return sections with at least one keyword match, sorted by match count

    This is intentionally simple and transparent — easy to audit and correct.
    """
    ppc = _load_ppc()
    text_lower = complaint_text.lower()
    # Tokenise complaint into individual words for partial-root matching
    words = set(re.split(r'\W+', text_lower))

    scored = []
    for section in ppc:
        keywords: List[str] = section.get("keywords", [])
        hits = 0
        for kw in keywords:
            kw_l = kw.lower()
            # 1. Direct substring match (catches "house theft", "زنا بالجبر")
            if kw_l in text_lower:
                hits += 1
            else:
                # 2. Root/stem match: check if any word in the text *starts with*
                #    the keyword or vice-versa (handles stole/steal, killed/kill)
                kw_root = kw_l.rstrip("eing").rstrip("ed")  # crude English stemmer
                if any(w.startswith(kw_root) or kw_root.startswith(w[:4])
                       for w in words if len(w) >= 4 and len(kw_root) >= 4):
                    hits += 1

        if hits > 0:
            scored.append({**section, "_hits": hits})

    # Sort: more keyword hits = higher relevance
    scored.sort(key=lambda x: x["_hits"], reverse=True)
    return scored[:5]  # Return top 5 at most


# ── System prompt ──────────────────────────────────────────────────────────────
_FIR_SYSTEM = """You are a legal document assistant specialising in Pakistani criminal law.
Your task is to draft a First Information Report (FIR) in the standard Pakistani police format.

RULES:
1. Use ONLY the facts provided by the complainant — do not add or invent details.
2. The FIR must be bilingual: English first, then Urdu translation below.
3. Cite the PPC sections identified by the system — explain each in simple Urdu.
4. Use formal, standard FIR language.
5. Include a clear note that this is a DRAFT for officer review and approval.
6. The Urdu must be in clear, simple language that any Urdu speaker can understand.

FIR FORMAT:
---
FIRST INFORMATION REPORT (FIR) — DRAFT FOR OFFICER REVIEW
Station: [Station Name if known, else leave blank]
Date: [today's date]
Section(s): [PPC sections]

COMPLAINT IN ENGLISH:
[formal FIR text based on the complainant's statement]

RELEVANT PPC SECTIONS:
[list each section with a brief plain-language explanation]

---
ایف آئی آر مسودہ (پولیس افسر کے جائزے کے لیے)
تاریخ: [آج کی تاریخ]
دفعات: [پی پی سی دفعات]

شکایت (اردو میں):
[اردو ترجمہ]

متعلقہ دفعات کی وضاحت:
[ہر دفعہ کی سادہ اردو وضاحت]

---
⚠️ DRAFT ONLY — Must be reviewed and signed by authorised police officer before filing.
⚠️ مسودہ — دائر کرنے سے پہلے مجاز پولیس افسر کا جائزہ اور دستخط ضروری ہیں۔
"""

_FIR_USER_TEMPLATE = """
COMPLAINANT'S STATEMENT:
{complaint}

IDENTIFIED PPC SECTIONS (from keyword analysis):
{sections_summary}

Please draft the bilingual FIR using the above information.
"""


def draft_fir(complaint_text: str) -> Dict[str, Any]:
    """
    Generate a bilingual FIR draft from a complainant's statement.

    Args:
        complaint_text: The complainant's description of the incident
                        (Urdu or English, any length).

    Returns:
        {
            "fir_draft":       str,          # bilingual FIR text
            "matched_sections":List[dict],   # PPC sections identified
            "complaint_text":  str,
            "disclaimer":      str,
        }
    """
    # Step 1 — Match PPC sections
    matched = _match_sections(complaint_text)

    # Build a summary of matched sections for the LLM prompt
    if matched:
        sections_summary = "\n".join(
            f"• Section {s['section']} PPC — {s['title']} "
            f"(Urdu: {s['urdu_title']})"
            for s in matched
        )
    else:
        sections_summary = (
            "No specific PPC sections identified automatically. "
            "The drafting officer should determine the appropriate sections."
        )

    # Step 2 — LLM generates the FIR
    user_msg = _FIR_USER_TEMPLATE.format(
        complaint=complaint_text,
        sections_summary=sections_summary,
    )

    fir_draft = chat(
        system_prompt=_FIR_SYSTEM,
        user_message=user_msg,
    )

    # Step 3 — Clean up matched sections for the response
    clean_sections = [
        {
            "section"          : s["section"],
            "title"            : s["title"],
            "urdu_title"       : s["urdu_title"],
            "description"      : s["description"],
            "urdu_description" : s["urdu_description"],
            "severity"         : s["severity"],
            "category"         : s["category"],
        }
        for s in matched
    ]

    return {
        "fir_draft"        : fir_draft,
        "matched_sections" : clean_sections,
        "complaint_text"   : complaint_text,
        "disclaimer"       : (
            "This FIR draft is AI-generated and for review purposes only. "
            "It must be reviewed, corrected, and approved by an authorised "
            "police officer before any official action is taken. "
            "یہ مسودہ صرف جائزے کے لیے ہے اور دائر کرنے سے پہلے مجاز افسر کی منظوری ضروری ہے۔"
        ),
    }
