# StadiumIQ

## Overview
StadiumIQ is a Streamlit-based AI stadium intelligence platform built for FIFA World Cup 2026 operations: fan assistance, crowd intelligence, accessibility routing, transport coordination, sustainability monitoring, and operations command. It uses Groq's Llama-3.3-70B model when a `GROQ_API_KEY` is configured, and automatically falls back to a high-fidelity local simulator (`services/simulator.py`) when no key is present, so the app is always fully functional.

## Running
- The `Start application` workflow runs `python3 run_app.py`, which launches Streamlit on port 5000 (required for the Replit webview).
- Without a `GROQ_API_KEY` secret, the app runs entirely in Demo/Simulation Mode — all six modules work with realistic synthetic data.
- To enable real LLM responses, add a `GROQ_API_KEY` secret (get one at https://console.groq.com/).

## Project structure
- `app.py` — entrypoint and page/sidebar layout
- `modules/` — one file per feature (fan assistant, crowd, accessibility, transport, sustainability, operations)
- `services/` — Groq client, prompt chains, output parsing, simulator fallback, conversation memory, shared UI utils
- `models/schemas.py` — Pydantic models for structured LLM output
- `tests/` — pytest suite covering the simulator, output parser, Groq client, and chain fallback behavior

## Recent changes (2026-07-11)
- Imported from GitHub; installed Python dependencies and configured the `Start application` workflow.
- Changed the Streamlit server port from 3000 to 5000 to match Replit's webview requirement.
- Cleaned up unused imports/variables (ruff) and confirmed no security findings (bandit) or hardcoded secrets.
- Verified the full pytest suite (18 tests) passes and the app renders correctly in Demo Mode.
