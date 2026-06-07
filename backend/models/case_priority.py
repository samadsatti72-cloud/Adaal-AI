# backend/models/case_priority.py
"""
AdaalAI — Module 3: Case Prioritization Engine
Uses XGBoost to score court cases by urgency.

Priority Labels:
  2 = HIGH   — needs immediate attention (under-trial detention, serious charge)
  1 = MEDIUM — should be heard soon
  0 = LOW    — routine scheduling

Features used:
  - charge_severity       (1=Low, 2=Medium, 3=High)
  - days_pending          (how long the case has been in court)
  - adjournments          (number of postponements)
  - is_under_trial        (1 if accused is in custody)
  - under_trial_days      (days in custody without conviction)
  - court_visits          (total hearings held)
  - adjournment_rate      (adjournments / court_visits — stalling indicator)
  - accused_age           (age of accused)
"""
from __future__ import annotations

import json
import os
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

from backend.core.config import settings


# ── Feature columns used by the model ─────────────────────────────────────────
FEATURE_COLS = [
    "charge_severity",
    "days_pending",
    "adjournments",
    "is_under_trial",
    "under_trial_days",
    "court_visits",
    "adjournment_rate",
    "accused_age",
]

PRIORITY_LABELS = {0: "Low", 1: "Medium", 2: "High"}

# Module-level model cache
_model: xgb.XGBClassifier | None = None


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to a case DataFrame."""
    df = df.copy()
    # Stalling indicator: ratio of adjournments to total hearings
    df["adjournment_rate"] = df["adjournments"] / (df["court_visits"] + 1)
    return df


def train(case_data_path: str | None = None) -> Dict[str, Any]:
    """
    Train the XGBoost case prioritization model and save it.

    Args:
        case_data_path: Path to cases.json. Uses settings default if None.

    Returns:
        Dict with accuracy metrics and feature importances.
    """
    path = case_data_path or settings.CASE_DATA_PATH
    with open(path, "r") as f:
        cases = json.load(f)

    df = pd.DataFrame(cases)
    df = _engineer_features(df)

    X = df[FEATURE_COLS]
    y = df["priority_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Save model
    os.makedirs(os.path.dirname(settings.MODEL_SAVE_PATH), exist_ok=True)
    model.save_model(settings.MODEL_SAVE_PATH)

    # Feature importances
    importances = dict(zip(FEATURE_COLS, model.feature_importances_.tolist()))

    print(f"[CasePriority] Model trained — accuracy: {report['accuracy']:.2%}")
    print(f"[CasePriority] Saved to {settings.MODEL_SAVE_PATH}")

    return {
        "accuracy"            : round(report["accuracy"], 4),
        "feature_importances" : importances,
        "report"              : report,
    }


def _load_model() -> xgb.XGBClassifier:
    """Lazy-load model from disk (trains from scratch if not found)."""
    global _model
    if _model is None:
        if not os.path.exists(settings.MODEL_SAVE_PATH):
            print("[CasePriority] No saved model found — training now...")
            train()
        m = xgb.XGBClassifier()
        m.load_model(settings.MODEL_SAVE_PATH)
        _model = m
    return _model


def score_case(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score a single case and return its priority.

    Args:
        case: Dict with fields matching FEATURE_COLS (plus case metadata).

    Returns:
        {
            "case_id":         str,
            "priority_label":  str,    # "High" / "Medium" / "Low"
            "priority_score":  int,    # 2 / 1 / 0
            "confidence":      float,  # model confidence 0–1
            "flags":           list,   # human-readable reasons
        }
    """
    model = _load_model()

    row = {col: case.get(col, 0) for col in FEATURE_COLS}
    row["adjournment_rate"] = row["adjournments"] / (row["court_visits"] + 1)

    df = pd.DataFrame([row])
    proba = model.predict_proba(df)[0]
    pred  = int(model.predict(df)[0])
    conf  = float(proba[pred])

    flags = _generate_flags(case)

    return {
        "case_id"       : case.get("case_id", "unknown"),
        "priority_label": PRIORITY_LABELS[pred],
        "priority_score": pred,
        "confidence"    : round(conf, 4),
        "probabilities" : {
            "Low"   : round(float(proba[0]), 4),
            "Medium": round(float(proba[1]), 4),
            "High"  : round(float(proba[2]), 4),
        },
        "flags"         : flags,
    }


def score_docket(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Score and rank a list of cases (a judge's docket).

    Args:
        cases: List of case dicts.

    Returns:
        List of scored cases sorted High → Medium → Low.
    """
    scored = [score_case(c) for c in cases]
    # Merge original case metadata with scores
    merged = [{**cases[i], **scored[i]} for i in range(len(cases))]
    # Sort: High first, then by days_pending descending
    merged.sort(key=lambda x: (-x["priority_score"], -x.get("days_pending", 0)))
    return merged


def _generate_flags(case: Dict) -> List[str]:
    """Generate plain-English flags explaining the priority reasons."""
    flags = []

    under_trial_days = case.get("under_trial_days", 0)
    days_pending     = case.get("days_pending", 0)
    adjournments     = case.get("adjournments", 0)
    charge_severity  = case.get("charge_severity", 1)
    court_visits     = case.get("court_visits", 1)

    if under_trial_days > 365:
        flags.append(
            f"⚠️ CONSTITUTIONAL ALERT: Accused in custody for {under_trial_days} days "
            "without conviction (exceeds 1 year). Article 10-A right to speedy trial at risk."
        )
    elif under_trial_days > 180:
        flags.append(
            f"Under-trial for {under_trial_days} days — bail review recommended."
        )

    if charge_severity == 3:
        flags.append("Serious charge (murder / rape / robbery) — high-severity case.")

    if days_pending > 730:
        flags.append(
            f"Case pending for {days_pending} days ({days_pending // 365} years) — "
            "significantly overdue."
        )

    adjournment_rate = adjournments / (court_visits + 1)
    if adjournment_rate > 0.7:
        flags.append(
            f"High adjournment rate ({adjournment_rate:.0%}) — possible delay tactics detected."
        )

    return flags


def is_model_trained() -> bool:
    """Check if the saved model file exists."""
    return os.path.exists(settings.MODEL_SAVE_PATH)
