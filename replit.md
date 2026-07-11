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
- Added `pyproject.toml` ruff config (E, F, W, I, UP, B); repo is 100% clean on `ruff check .`.
- Reviewed and justified the only 3 bandit findings with `# nosec` comments (fixed-argv subprocess launch, non-cryptographic cosmetic ID); `bandit -r . -x .pythonlibs,.git,tests` reports 0 issues.
- Added accessibility improvements: keyboard `:focus-visible` outlines, `prefers-reduced-motion` support, a skip-to-main-content link, `aria-hidden` on decorative emoji, and a `role="main"` landmark.
- Grew the pytest suite from 18 to 36 tests (added simulator scenario-branch coverage, demo-chat intent coverage, and utils rendering tests); added `pytest-cov` to `requirements.txt`. Coverage is 75% overall, 91%+ on the simulator and 100% on schemas/memory/output-parser-adjacent modules.
- Verified the app renders correctly in Demo Mode after every change.
