# ─────────────────────────────────────────────────────────────────────────────
#  AdaalAI — Legal Corpus Seed Data Builder
#  Generates: data/ppc_sections.json, data/judgments.json, data/cases.json
#  Run: python scripts/seed_data.py
# ─────────────────────────────────────────────────────────────────────────────
import json, os, random
from datetime import datetime, timedelta

os.makedirs("data", exist_ok=True)

# ── 1. PPC SECTIONS ──────────────────────────────────────────────────────────
# Core sections of the Pakistan Penal Code relevant to FIR drafting
PPC_SECTIONS = [
    {
        "section": "302",
        "title": "Punishment for Qatl-i-Amd (Murder)",
        "urdu_title": "قتل عمد کی سزا",
        "description": "Whoever commits qatl-i-amd shall be punished with death as qisas, or with imprisonment for life, or with imprisonment of either description which may extend to 25 years.",
        "urdu_description": "جو کوئی قتل عمد کرے اسے قصاص کے طور پر موت، یا عمر قید، یا 25 سال تک قید کی سزا دی جائے گی۔",
        "keywords": ["murder", "kill", "death", "qatl", "قتل", "مارنا", "ہلاک"],
        "category": "Against Person",
        "severity": "High"
    },
    {
        "section": "324",
        "title": "Attempt to commit qatl-i-amd",
        "urdu_title": "قتل عمد کی کوشش",
        "description": "Whoever does any act with such intention or knowledge and under such circumstances that if he thereby caused qatl, he would be guilty of qatl-i-amd.",
        "urdu_description": "جو کوئی قتل عمد کی کوشش کرے اسے 10 سال قید تک سزا ہو سکتی ہے۔",
        "keywords": ["attempt murder", "attack", "assault", "injury", "حملہ", "زخم", "تشدد"],
        "category": "Against Person",
        "severity": "High"
    },
    {
        "section": "354",
        "title": "Assault or criminal force on woman with intent to outrage modesty",
        "urdu_title": "عورت کی عزت پر حملہ",
        "description": "Whoever assaults or uses criminal force to any woman with intent to outrage her modesty, shall be punished with imprisonment not less than one year and not more than seven years.",
        "urdu_description": "جو کوئی کسی عورت پر حملہ کرے یا اس کی عزت کو نقصان پہنچانے کی نیت سے طاقت استعمال کرے، اسے ایک سے سات سال قید کی سزا ہوگی۔",
        "keywords": ["assault woman", "harass", "molest", "modesty", "عورت", "ہراساں", "چھیڑنا"],
        "category": "Against Woman",
        "severity": "High"
    },
    {
        "section": "376",
        "title": "Punishment for rape",
        "urdu_title": "زنا بالجبر کی سزا",
        "description": "Whoever commits rape shall be punished with imprisonment of either description for a term which shall not be less than ten years or more than twenty-five years and shall also be liable to fine.",
        "urdu_description": "جو کوئی زنا بالجبر کا ارتکاب کرے اسے کم از کم 10 اور زیادہ سے زیادہ 25 سال قید کی سزا ہوگی۔",
        "keywords": ["rape", "sexual assault", "zina", "زنا بالجبر", "جنسی زیادتی"],
        "category": "Against Woman",
        "severity": "Critical"
    },
    {
        "section": "379",
        "title": "Punishment for theft",
        "urdu_title": "چوری کی سزا",
        "description": "Whoever commits theft shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "urdu_description": "جو کوئی چوری کرے اسے تین سال تک قید یا جرمانہ یا دونوں سزائیں ہو سکتی ہیں۔",
        "keywords": ["theft", "steal", "robbery", "چوری", "چرانا", "ڈاکہ"],
        "category": "Property",
        "severity": "Medium"
    },
    {
        "section": "380",
        "title": "Theft in dwelling house",
        "urdu_title": "گھر میں چوری",
        "description": "Whoever commits theft in any building, tent or vessel which is used as a human dwelling shall be punished with imprisonment of either description for a term which may extend to seven years.",
        "urdu_description": "جو کوئی گھر، خیمے یا جہاز میں چوری کرے جو انسانی رہائش کے لیے استعمال ہو اسے سات سال تک قید کی سزا ہو سکتی ہے۔",
        "keywords": ["house theft", "burglary", "home", "ghar", "گھر میں چوری", "سیندھ"],
        "category": "Property",
        "severity": "Medium"
    },
    {
        "section": "392",
        "title": "Punishment for robbery",
        "urdu_title": "ڈکیتی کی سزا",
        "description": "Whoever commits robbery shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
        "urdu_description": "جو کوئی ڈکیتی کرے اسے دس سال تک سخت قید اور جرمانہ کی سزا ہو سکتی ہے۔",
        "keywords": ["robbery", "loot", "snatch", "dacoity", "ڈکیتی", "لوٹنا", "چھیننا"],
        "category": "Property",
        "severity": "High"
    },
    {
        "section": "406",
        "title": "Punishment for criminal breach of trust",
        "urdu_title": "امانت میں خیانت",
        "description": "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
        "urdu_description": "جو کوئی امانت میں خیانت کرے اسے تین سال تک قید یا جرمانہ یا دونوں کی سزا ہو سکتی ہے۔",
        "keywords": ["fraud", "breach trust", "embezzle", "khiyanat", "خیانت", "دھوکہ", "فراڈ"],
        "category": "Property",
        "severity": "Medium"
    },
    {
        "section": "420",
        "title": "Cheating and dishonestly inducing delivery of property",
        "urdu_title": "دھوکہ دہی",
        "description": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property shall be punished with imprisonment which may extend to seven years.",
        "urdu_description": "جو کوئی دھوکہ دہی کرے اور کسی کو بے ایمانی سے جائیداد دلوائے اسے سات سال تک قید کی سزا ہو سکتی ہے۔",
        "keywords": ["cheat", "fraud", "deceive", "dhoka", "دھوکہ", "فریب", "جعلسازی"],
        "category": "Property",
        "severity": "Medium"
    },
    {
        "section": "441",
        "title": "Criminal trespass",
        "urdu_title": "مجرمانہ تجاوز",
        "description": "Whoever enters into or upon property in the possession of another with intent to commit an offence, shall be punished with imprisonment for a term not exceeding three months.",
        "urdu_description": "جو کوئی کسی کی جائیداد میں جرم کی نیت سے داخل ہو اسے تین ماہ تک قید کی سزا ہو سکتی ہے۔",
        "keywords": ["trespass", "enter", "property", "land", "زمین", "تجاوز", "ناجائز قبضہ"],
        "category": "Property",
        "severity": "Low"
    },
    {
        "section": "447",
        "title": "Punishment for criminal trespass",
        "urdu_title": "مجرمانہ تجاوز کی سزا",
        "description": "Whoever commits criminal trespass shall be punished with imprisonment for a term not exceeding three months, or with fine not exceeding five hundred rupees, or both.",
        "urdu_description": "مجرمانہ تجاوز کرنے والے کو تین ماہ قید یا پانچ سو روپے جرمانہ یا دونوں سزائیں ہو سکتی ہیں۔",
        "keywords": ["trespass", "encroach", "illegal possession", "قبضہ", "ناجائز"],
        "category": "Property",
        "severity": "Low"
    },
    {
        "section": "498-A",
        "title": "Prohibition of depriving woman from inheriting property",
        "urdu_title": "عورت کو وراثت سے محروم کرنا",
        "description": "Whoever by deceitful or illegal means deprives a woman of her right of inheritance shall be punished with imprisonment which may extend to 10 years.",
        "urdu_description": "جو کوئی عورت کو وراثت کے حق سے محروم کرے اسے دس سال تک قید کی سزا ہو سکتی ہے۔",
        "keywords": ["inheritance", "property rights", "woman rights", "wirasat", "وراثت", "جائیداد", "حق"],
        "category": "Against Woman",
        "severity": "High"
    },
    {
        "section": "506",
        "title": "Punishment for criminal intimidation",
        "urdu_title": "دھمکی کی سزا",
        "description": "Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both.",
        "urdu_description": "جو کوئی مجرمانہ دھمکی دے اسے دو سال تک قید یا جرمانہ یا دونوں کی سزا ہو سکتی ہے۔",
        "keywords": ["threat", "intimidation", "blackmail", "dhamki", "دھمکی", "خوف", "بلیک میل"],
        "category": "Against Person",
        "severity": "Medium"
    },
    {
        "section": "511",
        "title": "Punishment for attempting to commit offences",
        "urdu_title": "جرم کی کوشش کی سزا",
        "description": "Whoever attempts to commit an offence punishable by imprisonment for life shall be punished with imprisonment for a term which may extend to one-half of the longest term provided for that offence.",
        "urdu_description": "جو کوئی کسی جرم کی کوشش کرے تو اسے اس جرم کی زیادہ سے زیادہ سزا کے نصف تک قید کی سزا ہو سکتی ہے۔",
        "keywords": ["attempt", "try", "koshish", "کوشش", "ناکام کوشش"],
        "category": "General",
        "severity": "Medium"
    }
]

# ── 2. SAMPLE JUDGMENTS ───────────────────────────────────────────────────────
JUDGMENTS = [
    {
        "id": "SC-2019-001",
        "court": "Supreme Court of Pakistan",
        "case_no": "Criminal Appeal No. 15 of 2019",
        "year": 2019,
        "parties": "Muhammad Azam vs. State",
        "section": "302",
        "outcome": "Conviction Upheld",
        "summary": "The Supreme Court upheld the conviction of the appellant under Section 302 PPC for committing murder. The court found that the prosecution had established the guilt beyond reasonable doubt through eyewitness testimony and forensic evidence. The death sentence was confirmed. Key principle: Benefit of doubt cannot be extended where direct witnesses are credible and corroborated by medical evidence.",
        "keywords": ["murder", "302", "death sentence", "eyewitness", "forensic", "conviction"],
        "judges": ["Justice Asif Saeed Khosa", "Justice Umar Ata Bandial"],
        "legal_principle": "Benefit of doubt must be genuine and reasonable, not based on remote possibility."
    },
    {
        "id": "LHC-2021-045",
        "court": "Lahore High Court",
        "case_no": "Crl. Appeal No. 45 of 2021",
        "year": 2021,
        "parties": "State vs. Imran Khan",
        "section": "379",
        "outcome": "Bail Granted",
        "summary": "The Lahore High Court granted bail to the accused charged under Section 379 PPC (theft). The court noted that the accused had been in custody for over 18 months without trial commencing, violating his fundamental right to a speedy trial under Article 10-A of the Constitution. The court emphasized that prolonged pre-trial detention without trial is unconstitutional.",
        "keywords": ["theft", "379", "bail", "under-trial", "article 10-a", "speedy trial", "fundamental rights"],
        "judges": ["Justice Sardar Ahmed Naeem"],
        "legal_principle": "Article 10-A guarantees right to fair trial. Prolonged under-trial detention without commencement of trial violates this right."
    },
    {
        "id": "SC-2020-088",
        "court": "Supreme Court of Pakistan",
        "case_no": "Const. Petition No. 88 of 2020",
        "year": 2020,
        "parties": "Shahida Bibi vs. State",
        "section": "354",
        "outcome": "Conviction Enhanced",
        "summary": "The Supreme Court enhanced the conviction and sentence in a case of assault on a woman. The court held that crimes against women must be dealt with utmost severity. The trial court sentence was enhanced from 1 year to 5 years. The court directed all lower courts to prioritize cases involving violence against women.",
        "keywords": ["assault woman", "354", "sentence enhancement", "violence against women", "priority"],
        "judges": ["Justice Gulzar Ahmed", "Justice Mushir Alam"],
        "legal_principle": "Courts must prioritize cases involving violence against women. Inadequate sentencing sends wrong signals to society."
    },
    {
        "id": "PHC-2022-012",
        "court": "Peshawar High Court",
        "case_no": "Crl. Misc. No. 12 of 2022",
        "year": 2022,
        "parties": "Ahmed Gul vs. Muhammad Tariq",
        "section": "447",
        "outcome": "Acquittal",
        "summary": "The Peshawar High Court acquitted the accused charged with criminal trespass under Section 447 PPC. The court found that the complainant failed to establish legal possession of the property. The court emphasized that for conviction under Section 447, the prosecution must prove that the complainant had valid possession and the accused entered with criminal intent.",
        "keywords": ["trespass", "447", "acquittal", "possession", "criminal intent", "property"],
        "judges": ["Justice Ishtiaq Ibrahim"],
        "legal_principle": "Prosecution must prove both lawful possession of the complainant AND criminal intent of the accused for conviction under Section 447."
    },
    {
        "id": "SHC-2021-199",
        "court": "Sindh High Court",
        "case_no": "Crl. Appeal No. 199 of 2021",
        "year": 2021,
        "parties": "Ghulam Mustafa vs. State",
        "section": "406",
        "outcome": "Conviction Upheld",
        "summary": "The Sindh High Court upheld the conviction of the appellant under Section 406 PPC for criminal breach of trust. The accused, a cashier, had misappropriated Rs. 2.4 million of company funds. The court found that documentary evidence in the form of account books and bank statements were sufficient to establish the offence beyond doubt.",
        "keywords": ["breach of trust", "406", "misappropriation", "embezzlement", "financial", "documentary evidence"],
        "judges": ["Justice Salahuddin Panhwar", "Justice Amjad Ali Sahito"],
        "legal_principle": "In cases of financial fraud, documentary evidence such as account books and bank statements can be sufficient for conviction without eyewitnesses."
    },
    {
        "id": "SC-2023-034",
        "court": "Supreme Court of Pakistan",
        "case_no": "Criminal Petition No. 34 of 2023",
        "year": 2023,
        "parties": "Nasreen Akhtar vs. Collector Land Revenue",
        "section": "498-A",
        "outcome": "Landmark Ruling — FIR Registration Ordered",
        "summary": "A landmark judgment where the Supreme Court directed the registration of FIR against relatives of the complainant who had deprived her of her inheritance from her deceased father. The court held that women's right to inheritance is a fundamental right protected by both Islam and the Constitution of Pakistan. The police were directed to register the FIR within 48 hours.",
        "keywords": ["inheritance", "498-A", "women rights", "FIR registration", "police duty", "fundamental rights", "wirasat"],
        "judges": ["Chief Justice Qazi Faez Isa", "Justice Yahya Afridi"],
        "legal_principle": "Police officers have a mandatory duty to register FIR where a cognizable offence is disclosed. Refusal to register FIR is itself an offence."
    },
    {
        "id": "LHC-2023-201",
        "court": "Lahore High Court",
        "case_no": "Crl. Misc. No. 201 of 2023",
        "year": 2023,
        "parties": "Bushra Naz vs. Hafeez Ahmed",
        "section": "506",
        "outcome": "Bail Rejected",
        "summary": "The Lahore High Court rejected bail for the accused in a criminal intimidation case. The accused had repeatedly threatened the complainant via phone calls. The court noted that the threats were recorded and verified. The court distinguished this case from ordinary criminal intimidation as the threats involved potential violence and the accused had prior criminal record.",
        "keywords": ["threat", "criminal intimidation", "506", "bail rejected", "phone threats", "prior record"],
        "judges": ["Justice Tariq Saleem Sheikh"],
        "legal_principle": "Bail may be denied where there is credible evidence that the accused poses a continuing threat to the complainant or witnesses."
    },
    {
        "id": "SC-2022-156",
        "court": "Supreme Court of Pakistan",
        "case_no": "Const. Petition No. 156 of 2022",
        "year": 2022,
        "parties": "Human Rights Case — Prison Reform",
        "section": "General",
        "outcome": "Suo Motu — Prison Reform Ordered",
        "summary": "The Supreme Court took suo motu notice of the condition of under-trial prisoners in Pakistan's jails. The court found that 66% of prison population were under-trial prisoners, many awaiting trial for 2-5 years. The court directed all High Courts to constitute special benches to dispose of under-trial cases. Directed creation of a monitoring system for under-trial prisoners detained over 6 months.",
        "keywords": ["under-trial", "prison reform", "human rights", "speedy trial", "article 10-A", "fundamental rights", "suo motu"],
        "judges": ["Chief Justice Umar Ata Bandial"],
        "legal_principle": "State has a constitutional obligation under Article 10-A to ensure speedy trial. Mass under-trial detention is a constitutional crisis requiring systematic judicial intervention."
    }
]

# ── 3. SYNTHETIC CASE DATA FOR ML MODEL ──────────────────────────────────────
CHARGES_HIGH   = ["302", "376", "324", "392", "34+302"]
CHARGES_MEDIUM = ["354", "406", "420", "498-A", "506"]
CHARGES_LOW    = ["379", "380", "441", "447", "511"]
COURTS         = ["District Court Lahore", "District Court Karachi", "District Court Rawalpindi",
                  "District Court Faisalabad", "District Court Peshawar", "District Court Quetta"]
STATUSES       = ["Under Trial", "Evidence Stage", "Arguments Stage", "Reserved for Judgment",
                  "Hearing Adjourned", "Pending Investigation"]

random.seed(42)

cases = []
for i in range(200):
    charge_type = random.choices(["high", "medium", "low"], weights=[0.3, 0.4, 0.3])[0]
    if charge_type == "high":
        charge  = random.choice(CHARGES_HIGH)
        severity = 3
    elif charge_type == "medium":
        charge  = random.choice(CHARGES_MEDIUM)
        severity = 2
    else:
        charge  = random.choice(CHARGES_LOW)
        severity = 1

    days_pending     = random.randint(30, 1500)
    adjournments     = random.randint(0, int(days_pending / 45))
    under_trial_days = days_pending if random.random() < 0.65 else 0
    court_visits     = random.randint(1, adjournments + 1)
    accused_age      = random.randint(18, 70)

    # Label: priority 2=High, 1=Medium, 0=Low
    # Rules: long detention + serious charge → High
    if under_trial_days > 365 or (severity == 3 and days_pending > 180):
        label = 2
    elif days_pending > 300 or severity == 2:
        label = 1
    else:
        label = 0

    cases.append({
        "case_id"          : f"ADL-2024-{i+1:04d}",
        "court"            : random.choice(COURTS),
        "charge_section"   : charge,
        "charge_severity"  : severity,
        "days_pending"     : days_pending,
        "adjournments"     : adjournments,
        "under_trial_days" : under_trial_days,
        "is_under_trial"   : 1 if under_trial_days > 0 else 0,
        "court_visits"     : court_visits,
        "accused_age"      : accused_age,
        "status"           : random.choice(STATUSES),
        "priority_label"   : label
    })

# ── WRITE ALL DATA ─────────────────────────────────────────────────────────────
with open("data/ppc_sections.json", "w", encoding="utf-8") as f:
    json.dump(PPC_SECTIONS, f, ensure_ascii=False, indent=2)

with open("data/judgments.json", "w", encoding="utf-8") as f:
    json.dump(JUDGMENTS, f, ensure_ascii=False, indent=2)

with open("data/cases.json", "w", encoding="utf-8") as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)

print(f"✅  Seeded {len(PPC_SECTIONS)} PPC sections → data/ppc_sections.json")
print(f"✅  Seeded {len(JUDGMENTS)} judgments       → data/judgments.json")
print(f"✅  Seeded {len(cases)} case records       → data/cases.json")
