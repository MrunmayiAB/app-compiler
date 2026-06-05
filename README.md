# App Compiler

A multi-stage pipeline that converts natural language descriptions into complete, validated app specifications — database schema, API endpoints, UI layout, and auth rules.

## Architecture
User Prompt → Stage 1 (Intent) → Stage 2 (Design) → Stage 3 (Schemas) → Stage 4 (Validation) → Output
## Why Multi-Stage?

A single prompt approach is unreliable. This pipeline treats app generation like a compiler — each stage has one job, strict input/output contracts, and the next stage builds on verified output from the previous one.

## Pipeline Stages

**Stage 1 — Intent Extraction:** Parses natural language into structured intent: app type, features, entities, roles, constraints, ambiguities.

**Stage 2 — System Design:** Converts intent into architecture: modules, entity relationships, user flows, auth strategy.

**Stage 3 — Schema Generation:** Generates DB schema, API schema, UI schema, and Auth rules simultaneously.

**Stage 4 — Validation and Repair:** Runs rule-based checks across all layers. If issues found, repairs only the broken parts — not a full retry.

## Execution Awareness

executor.py takes the final JSON and produces real runnable files — schema.sql and api.py FastAPI stubs.

## Setup

1. Clone the repo
2. Create a virtual environment and install dependencies: pip install google-genai pydantic streamlit python-dotenv
3. Create a .env file with your GEMINI_API_KEY
4. Run: streamlit run app.py

## Evaluation

Tested on 20 prompts — 10 normal, 10 edge cases (vague, conflicting, incomplete, ambiguous). Results in evaluation_results.csv.

## Tech Stack

- LLM: Google Gemini (gemini-3.5-flash)
- Validation: rule-based checks + LLM repair
- UI: Streamlit
- Execution: SQL + FastAPI stub generation
