# backend/core/llm_client.py
"""
AdaalAI — LLM Client
Supports Groq (free, recommended) and OpenAI.
Falls back to offline demo mode when no API key is configured.
"""
import datetime
from openai import OpenAI
from backend.core.config import settings


def _build_client() -> OpenAI:
    if settings.LLM_PROVIDER == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("NO_KEY")
        return OpenAI(api_key=settings.GROQ_API_KEY,
                      base_url="https://api.groq.com/openai/v1")
    else:
        if not settings.OPENAI_API_KEY:
            raise ValueError("NO_KEY")
        return OpenAI(api_key=settings.OPENAI_API_KEY)


def _demo_response(system_prompt: str, user_message: str) -> str:
    """Offline demo responses — detected by unique markers in each module's system prompt."""
    msg  = user_message.lower()
    today = datetime.date.today().strftime("%B %d, %Y")

    # ── FIR Draft (marker: "bilingual FIR draft") ─────────────────────────────
    if "bilingual FIR draft" in system_prompt or "standard SHO FIR format" in system_prompt:
        return f"""FIRST INFORMATION REPORT (FIR) — DRAFT FOR OFFICER REVIEW
Station: _______________
Date: {today}
Section(s): As identified by system

COMPLAINT IN ENGLISH:
The complainant appeared before the undersigned and stated that the described offence
was committed against them. The complainant requests registration of this FIR and
appropriate legal action against the accused under the relevant provisions of the
Pakistan Penal Code (as identified by the AI section-matching system above).

RELEVANT PPC SECTIONS:
The PPC sections listed above have been identified based on the complainant's statement.
Each section carries penalties as described. The officer should verify and confirm the
appropriate sections before official filing.

---
ایف آئی آر مسودہ (پولیس افسر کے جائزے کے لیے)
تاریخ: {today}

شکایت (اردو میں):
شاکی نے بیان دیا کہ ان کے ساتھ مندرجہ ذیل واقعہ پیش آیا۔ شاکی نے درخواست کی کہ
متعلقہ پی پی سی دفعات کے تحت ایف آئی آر درج کی جائے اور ملزم کے خلاف قانونی
کارروائی عمل میں لائی جائے۔

متعلقہ دفعات: اوپر درج شدہ دفعات کی تصدیق افسر کریں۔

---
⚠️ DRAFT ONLY — Must be reviewed and signed by an authorised police officer before filing.
⚠️ مسودہ — دائر کرنے سے پہلے مجاز پولیس افسر کا جائزہ اور دستخط ضروری ہیں۔

[DEMO MODE — Add GROQ_API_KEY to .env for full AI-generated bilingual FIR content]"""

    # ── Citizen Chatbot (marker: "AdaalAI Citizen Assistant") ─────────────────
    if "AdaalAI Citizen Assistant" in system_prompt:
        if "bail" in msg or "ضمانت" in msg:
            return """آپ کے ضمانت کے حقوق | YOUR BAIL RIGHTS:

اردو:
• ضمانتی جرائم میں پولیس کو فوری ضمانت دینی ہوگی — وہ انکار نہیں کر سکتی
• غیر ضمانتی جرائم میں صرف عدالت ضمانت دے سکتی ہے
• اگر 6 ماہ بعد بھی مقدمہ شروع نہ ہو تو ضمانت کی درخواست دی جا سکتی ہے
• نچلی عدالت انکار کرے تو ہائی کورٹ سے ضمانت مانگ سکتے ہیں

English:
• Bailable offences: Police MUST grant bail — they have no discretion to refuse
• Non-bailable offences: Only a court/magistrate can grant bail
• Under-trial 6+ months with no trial start: apply for bail on surety (Section 497 CrPC)
• High Court bail: available if lower court refuses

مفت قانونی امداد | Free Legal Aid:
• AGHS Lahore: 042-35761999   • HRCP: 051-9214536

For your specific situation, please consult a qualified lawyer.
[DEMO MODE — Add GROQ_API_KEY to .env for full AI responses]"""

        if "fir" in msg or "ایف آئی آر" in msg or "police" in msg or "complaint" in msg:
            return """ایف آئی آر کیسے درج کروائیں | HOW TO FILE AN FIR:

اردو:
• قریبی تھانے جائیں — کوئی بھی تھانہ آپ کی ایف آئی آر لے سکتا ہے
• ایس ایچ او کی قانونی ذمہ داری ہے کہ وہ ایف آئی آر درج کرے (دفعہ 154 CrPC)
• انکار کریں تو: DSP/SP سے شکایت، یا مجسٹریٹ کے پاس جائیں (دفعہ 190 CrPC)
• دستخط سے پہلے ایف آئی آر آپ کو پڑھ کر سنائی جائے
• آپ کو ایف آئی آر کی مفت کاپی ملنے کا حق ہے

English:
• Go to the nearest police station — any station can receive your FIR
• The SHO has a MANDATORY duty to register FIR (Section 154 CrPC)
• If refused: complain to DSP/SP, or apply to Magistrate (Section 190 CrPC)
• FIR must be read back to you before you sign it
• You are entitled to a FREE copy of the registered FIR

For your specific situation, please consult a qualified lawyer.
[DEMO MODE — Add GROQ_API_KEY to .env for full AI responses]"""

        if "arrest" in msg or "گرفتاری" in msg or "حقوق" in msg or "rights" in msg:
            return """گرفتاری کے وقت آپ کے حقوق | YOUR RIGHTS UPON ARREST:

اردو:
• گرفتاری کی وجہ جاننے کا حق (آئین کا آرٹیکل 10)
• گرفتاری کے فوراً بعد اپنے وکیل سے مشورہ کرنے کا حق
• 24 گھنٹے کے اندر مجسٹریٹ کے سامنے پیش کیے جانے کا حق
• خاموش رہنے کا حق — پولیس کے سوالات کا جواب دینا ضروری نہیں
• تشدد سے تحفظ کا حق — پولیس کی طرف سے تشدد سنگین جرم ہے

English:
• Right to know the reason for arrest (Article 10, Constitution of Pakistan)
• Right to consult a lawyer of your choice immediately after arrest
• Right to be produced before a magistrate within 24 hours of arrest
• Right to remain silent — you need not answer self-incriminating questions
• Right to humane treatment — police torture is a criminal offence (Section 337 PPC)

مفت قانونی امداد | Free Legal Aid:
• AGHS Lahore: 042-35761999   • HRCP: 051-9214536   • Women Helpline: 1099

For your specific situation, please consult a qualified lawyer.
[DEMO MODE — Add GROQ_API_KEY to .env for full AI responses]"""

        return """قانونی معلومات | LEGAL INFORMATION:

اردو: آپ کسی بھی قانونی معاملے کے بارے میں پوچھ سکتے ہیں — گرفتاری، ضمانت،
ایف آئی آر، خواتین کے حقوق، یا کوئی بھی قانونی سوال۔

English: I can help with any legal question — arrest rights, bail, FIR filing,
women's rights, property rights, or any other legal matter in Pakistan.

Try asking:
• "What are my rights when arrested?"
• "How do I file an FIR?"
• "What are bail rights?"
• "میری گرفتاری کے وقت میرے کیا حقوق ہیں؟"

مفت قانونی امداد | Free Legal Aid: AGHS 042-35761999 | HRCP 051-9214536

For your specific situation, please consult a qualified lawyer.
[DEMO MODE — Add GROQ_API_KEY to .env for full AI responses]"""

    # ── Legal Research (default) ───────────────────────────────────────────────
    return """Based on the retrieved Pakistani court judgments:

**Direct Answer:**
The retrieved cases provide relevant guidance on your query. Key principles established
by Pakistan's superior courts are summarised below.

**Key Legal Principles:**
1. Article 10-A of the Constitution of Pakistan guarantees the fundamental right to a
   fair trial and due process — courts consistently uphold this against prolonged delays
2. Prolonged under-trial detention without commencement of trial violates fundamental rights;
   courts have directed special benches to address this crisis (SC 2022)
3. Prosecution must establish guilt beyond reasonable doubt — any credible doubt benefits
   the accused (standard applied consistently across all court levels)
4. Police have a mandatory duty under Section 154 CrPC to register FIR for cognizable
   offences; refusal is itself an actionable offence

**Retrieved Case Citations:**
Please review the case cards below — each is drawn from actual Pakistani court records
and directly relevant to your query.

**Important Caveat:**
Always verify all citations against the original reported decisions in PLJ/PLD volumes
before relying on them in court or legal documents.

---
*AdaalAI: AI-assisted legal research — not a substitute for legal advice.*
*Consult a qualified advocate for your specific situation.*

[DEMO MODE — Add your free GROQ_API_KEY to .env to get full Llama 3 AI answers]"""


def chat(system_prompt: str, user_message: str, temperature: float | None = None) -> str:
    """Send a chat request. Falls back to demo mode on any error."""
    try:
        client = _build_client()
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return _demo_response(system_prompt, user_message)
