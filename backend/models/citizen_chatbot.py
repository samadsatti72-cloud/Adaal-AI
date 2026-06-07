# backend/models/citizen_chatbot.py
"""
AdaalAI — Module 4: Citizen Justice Chatbot (Urdu-first)
Answers questions about legal rights in plain Urdu and English.
Uses LLM with a Pakistani-law knowledge base as context.
No hallucination: only information from the embedded legal knowledge base.
"""
from __future__ import annotations

import json
from typing import Dict, Any, List

from backend.core.config import settings
from backend.core.llm_client import chat


# ── Static legal rights knowledge base ────────────────────────────────────────
LEGAL_RIGHTS_KB = """
=== YOUR RIGHTS WHEN ARRESTED (Pakistan) ===
- Right to know reason for arrest (Article 10, Constitution of Pakistan)
- Right to consult a lawyer of your choice immediately after arrest
- Right to be produced before a magistrate within 24 hours of arrest
- Right to bail in bailable offences — the police MUST grant bail
- Right not to be held in police custody for more than 24 hours without magistrate's order
- Right to remain silent — you do not have to answer questions that may incriminate you
- Right to humane treatment — torture and abuse by police is illegal under Section 337 PPC

=== گرفتاری کے وقت آپ کے حقوق ===
- گرفتاری کی وجہ جاننے کا حق (آئین کا آرٹیکل 10)
- گرفتاری کے فوراً بعد اپنی پسند کے وکیل سے مشورہ کرنے کا حق
- گرفتاری کے 24 گھنٹے کے اندر مجسٹریٹ کے سامنے پیش کیے جانے کا حق
- ضمانت کے قابل جرائم میں ضمانت کا حق — پولیس کو ضمانت دینی ہوگی
- مجسٹریٹ کے حکم کے بغیر 24 گھنٹے سے زیادہ پولیس حراست میں نہ رکھا جائے
- خاموش رہنے کا حق — آپ کو وہ سوالات جواب دینا ضروری نہیں جو آپ کے خلاف ہوں
- انسانی سلوک کا حق — پولیس کی طرف سے تشدد غیر قانونی ہے

=== HOW TO FILE AN FIR ===
- Go to the nearest police station (any station can receive your FIR)
- The SHO (Station House Officer) has a LEGAL DUTY to register your FIR if a cognizable offence is reported
- If police refuses, you can:
  1. Go to the District Superintendent of Police (DSP/SP) 
  2. File a complaint directly with the Magistrate (Section 190 CrPC)
  3. File a constitutional petition in High Court
- Your FIR must be read back to you before you sign it
- You are entitled to a FREE copy of the FIR

=== ایف آئی آر کیسے درج کروائیں ===
- قریبی تھانے جائیں (کوئی بھی تھانہ آپ کی ایف آئی آر لے سکتا ہے)
- ایس ایچ او کی قانونی ذمہ داری ہے کہ وہ ایف آئی آر درج کرے
- اگر پولیس انکار کرے تو: DSP/SP سے شکایت کریں، یا مجسٹریٹ کے پاس جائیں
- دستخط سے پہلے ایف آئی آر آپ کو پڑھ کر سنائی جائے
- آپ کو ایف آئی آر کی مفت کاپی ملنے کا حق ہے

=== BAIL RIGHTS ===
- Bailable offences: You have an absolute right to bail. Police cannot refuse.
- Non-bailable offences: Only a court/magistrate can grant bail.
- Under-trial prisoners: If trial has not started after 6 months, you can apply for bail on surety.
- High Court bail: If lower court refuses, you can apply to the High Court.

=== ضمانت کے حقوق ===
- ضمانتی جرائم: آپ کا ضمانت کا قطعی حق ہے، پولیس انکار نہیں کر سکتی
- غیر ضمانتی جرائم: صرف عدالت ضمانت دے سکتی ہے
- زیر سماعت قیدی: اگر 6 ماہ بعد بھی مقدمہ شروع نہ ہو تو ضمانت کی درخواست دی جا سکتی ہے

=== FREE LEGAL AID ===
- District Legal Empowerment Committee (DLEC): Available in all districts
- Pakistan Bar Council Legal Aid: Contact your district bar association
- Lawyers for Human Rights and Legal Aid (LHRLA): 021-111-001-001
- AGHS Legal Aid Cell Lahore: 042-35761999
- Human Rights Commission of Pakistan (HRCP): 051-9214536

=== مفت قانونی امداد ===
- ڈسٹرکٹ لیگل ایمپاورمنٹ کمیٹی (DLEC): تمام اضلاع میں دستیاب
- پاکستان بار کونسل: اپنی ضلعی بار ایسوسی ایشن سے رابطہ کریں
- AGHS قانونی امداد سیل لاہور: 042-35761999
- ہیومن رائٹس کمیشن: 051-9214536

=== WOMEN'S RIGHTS ===
- A woman cannot be arrested between sunset and sunrise (except in exceptional cases with female officer present)
- Female accused must be searched by a female police officer only
- Medical examination of rape survivors must be done by a female doctor
- Domestic violence is an offence under the Domestic Violence Act
- Women can file FIR at any police station — they do not need to return to the crime district

=== خواتین کے حقوق ===
- خاتون کو غروب آفتاب کے بعد اور طلوع آفتاب سے پہلے گرفتار نہیں کیا جا سکتا
- خاتون ملزمہ کی تلاشی صرف خاتون پولیس افسر لے سکتی ہے
- گھریلو تشدد قانون کے تحت ایک جرم ہے
- خواتین کسی بھی تھانے میں ایف آئی آر درج کروا سکتی ہیں
"""

# ── System prompt ──────────────────────────────────────────────────────────────
_CHATBOT_SYSTEM = """You are AdaalAI Citizen Assistant — a helpful, compassionate legal guidance 
assistant for Pakistani citizens.

Your role:
- Explain legal rights in simple, clear language that anyone can understand
- Always respond in BOTH Urdu AND English (Urdu first, then English)
- Be empathetic — people reaching out often face difficult situations
- Point to specific laws and rights rather than vague advice
- Always recommend consulting a lawyer for specific cases
- For emergencies or serious situations, provide relevant helpline numbers

KNOWLEDGE BASE (USE THIS AS YOUR SOURCE):
{knowledge_base}

CRITICAL RULES:
1. Only provide information based on the knowledge base above
2. If you don't know something, say so clearly — do not guess
3. Never provide specific legal advice for individual cases — direct to a lawyer
4. Always end with: "For your specific situation, please consult a lawyer."
5. Emergency situations (violence, immediate threat): provide emergency numbers (15 = Police, 1122 = Rescue)
"""

_CHATBOT_USER_TEMPLATE = """
User's question: {question}

Please respond helpfully in both Urdu and English.
"""


def answer(question: str) -> Dict[str, Any]:
    """
    Answer a citizen's legal question.

    Args:
        question: The citizen's question (Urdu or English).

    Returns:
        {
            "answer":    str,   # bilingual answer
            "question":  str,
            "emergency": bool,  # True if question suggests urgent situation
        }
    """
    # Detect emergency keywords
    emergency_keywords = [
        "help", "مدد", "emergency", "ایمرجنسی", "danger", "خطرہ",
        "beat", "مار", "violence", "تشدد", "threat", "دھمکی",
        "rape", "زیادتی", "kidnap", "اغوا", "murder", "قتل"
    ]
    is_emergency = any(kw in question.lower() for kw in emergency_keywords)

    system = _CHATBOT_SYSTEM.format(knowledge_base=LEGAL_RIGHTS_KB)
    user_msg = _CHATBOT_USER_TEMPLATE.format(question=question)

    response = chat(system_prompt=system, user_message=user_msg)

    if is_emergency:
        response += (
            "\n\n---\n"
            "🚨 EMERGENCY CONTACTS | ہنگامی رابطے:\n"
            "• Police Emergency: 15 | پولیس ایمرجنسی: 15\n"
            "• Rescue: 1122\n"
            "• Women Helpline: 1099\n"
            "• Child Protection: 1121"
        )

    return {
        "answer"   : response,
        "question" : question,
        "emergency": is_emergency,
    }
