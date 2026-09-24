# AI Network Threat Detection & Response System (AI-NTDRS)

AI-NTDRS is a cybersecurity platform for authorized network-flow monitoring, explainable ML-based threat detection, risk scoring, alert management, and safe response simulation for educational institutions.

## Current Status

- Phase 1: Requirements and system design specification complete.
- Phase 2: Research findings complete.
- Phase 3: Architecture overview complete.
- Phase 4: Backend implemented through auth, core APIs, copilot, and demo data seeding.
- Phase 5: ML pipeline scaffolded with preprocessing, baseline training, evaluation, and explainability hooks.
- Phase 6: Frontend implemented with login, dashboard, devices, alerts, incidents, reports, audit logs, and AI Copilot views.
- Testing and cleanup: Static validation and frontend production build pass. Automated Python tests are defined but could not be executed in this environment because Python is not on PATH.

## Repository Layout

- `backend/` - FastAPI backend and ML service integration.
- `frontend/` - React + TypeScript SOC dashboard.
- `docs/` - Specification, research, and architecture documents.
- `simulation/` - Safe demo traffic generation.
- `tests/` - Backend, API, and ML tests.

## Next Step

Expand endpoint filtering, refine copilot grounding, and add runtime test execution in an environment with Python available.

## Local AI Copilot

The Copilot can use a local Ollama model for conversational, SOC-grounded replies.
Install Ollama, then run `ollama pull qwen3.5:4b`. The default backend settings use
`http://127.0.0.1:11434` and `qwen3.5:4b`; override them with `OLLAMA_BASE_URL`
and `OLLAMA_MODEL` if needed. If Ollama or the model is unavailable, the API
returns the built-in SOC guidance and marks the response as a fallback. Security
context is sent only to the configured local Ollama service.
