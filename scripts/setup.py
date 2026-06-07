#!/usr/bin/env python3
"""
AdaalAI — First-Time Setup Script
Run this ONCE before starting the server.

What it does:
  1. Creates the data directory
  2. Seeds all legal data (PPC sections, judgments, case records)
  3. Builds the ChromaDB vector index from judgments
  4. Trains the XGBoost case prioritization model

Usage:
  cd adaalai
  python scripts/setup.py
"""
import sys, os

# Make sure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def step(msg: str):
    print(f"\n{'─'*60}")
    print(f"  {msg}")
    print('─'*60)


def main():
    print("\n" + "═"*60)
    print("  AdaalAI — Setup")
    print("  AI-Powered Judicial Assistance for Pakistan")
    print("═"*60)

    # ── Step 1: Seed data ──────────────────────────────────────────────────────
    step("Step 1/3: Generating legal corpus data...")
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    exec(open("scripts/seed_data.py").read())

    # ── Step 2: Build vector index ─────────────────────────────────────────────
    step("Step 2/3: Building ChromaDB judgment vector index...")
    print("  Note: First run downloads the embedding model (~1.1 GB). Please wait.")
    from backend.core.vector_store import build_index
    count = build_index()
    print(f"  ✅  Indexed {count} judgments into ChromaDB")

    # ── Step 3: Train XGBoost model ────────────────────────────────────────────
    step("Step 3/3: Training XGBoost case prioritization model...")
    from backend.models.case_priority import train
    metrics = train()
    print(f"  ✅  Model trained — Accuracy: {metrics['accuracy']:.1%}")
    print(f"  Top feature importances:")
    sorted_fi = sorted(metrics["feature_importances"].items(), key=lambda x: -x[1])
    for feat, imp in sorted_fi[:5]:
        print(f"    {feat:<25} {imp:.4f}")

    # ── Done ───────────────────────────────────────────────────────────────────
    print("\n" + "═"*60)
    print("  ✅  Setup Complete!")
    print("═"*60)
    print()
    print("  Next step: add your GROQ_API_KEY to .env, then run:")
    print()
    print("    cp .env.example .env")
    print("    # Edit .env and add your GROQ_API_KEY")
    print("    python -m uvicorn backend.api.main:app --reload --port 8000")
    print()
    print("  Then open: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
