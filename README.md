# HoloLens Jarvis

A personal, holographic AI assistant for Microsoft HoloLens 2 — voice in,
holographic panel out, backed by Claude, GPT, Gemini, or a self-hosted
agent (e.g. Hermes Agent) running on a PC on your LAN.

Personal side project. Single-user. Not for distribution.

## Why

HoloLens 2 is the only consumer-owned device capable of true stereo
holographic rendering — a categorically different experience than the
flat, single-eye HUD overlays available on current smart glasses
(Even Realities G2, Meta Ray-Ban Display, etc.). This project puts an
otherwise-unused HoloLens 2 to work as a personal Jarvis-style assistant.

## Status

🚧 Early planning / build stage. See `docs/BUILD_PLAN.md` for current
phase.

## Docs

- [`docs/PRD.md`](docs/PRD.md) — what this is, why, architecture, scope
- [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) — step-by-step execution
  checklist, in build order

## Repo layout

```
unity-client/     Unity 2022 LTS + MRTK 2.8 project (UWP/HoloLens 2 client)
backend/          Python WebSocket relay + LLM provider integrations
scripts/          Setup/dev helper scripts
docs/             PRD, build plan, notes
```

## Toolchain (pinned — see PRD for why)

- Unity 2022 LTS (not latest — HoloLens 2 support was dropped from new
  Unity releases after June 23, 2025)
- MRTK 2.8 (not MRTK3 — Microsoft currently recommends 2.8 for HoloLens 2)
- OpenXR, UWP/ARM64 build target
- Python 3.11+ for the backend relay

## Quick start

Backend:
```
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp config/config.example.yaml config/config.yaml
# edit config.yaml with your LLM API key
python relay/server.py
```

Unity client: open `unity-client/` in Unity 2022 LTS, see
`docs/BUILD_PLAN.md` Phase 0–1 for full MRTK setup steps.

## License

Personal project — no license file added yet; treat as all-rights-reserved
until you decide otherwise.
