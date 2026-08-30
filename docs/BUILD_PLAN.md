# Build Plan — HoloLens Jarvis

Companion to PRD.md. This is the step-by-step execution checklist, ordered
so each step produces something testable before moving to the next.

---

## Phase 0 — Environment Setup

- [ ] Confirm HoloLens 2 (not 1st gen) — check Settings > System > About
- [ ] Update HoloLens 2 to latest Windows Holographic OS version
- [ ] Enable Developer Mode on HoloLens (Settings > Update & Security >
      For Developers)
- [ ] Install Unity Hub
- [ ] Install Unity 2022 LTS specifically (NOT latest) via Unity Hub —
      check exact last-supported patch version against Microsoft Learn's
      HoloLens 2 Unity page before installing, versions listed there can
      change
- [ ] Install Visual Studio 2022 with:
  - Universal Windows Platform development workload
  - Game development with C++ workload (for IL2CPP)
- [ ] Install Windows 10/11 SDK (matching what VS installer recommends)
- [ ] Install the Mixed Reality Feature Tool from Microsoft
- [ ] Confirm dev machine and HoloLens are on the same LAN/Wi-Fi network
- [ ] Pair HoloLens with dev PC via Windows Device Portal (enable in
      headset settings, note its IP address)

**Checkpoint:** Windows Device Portal loads in a browser on your PC at
the HoloLens's IP address, showing device status.

---

## Phase 1 — Empty MRTK Project Deploys Successfully

- [ ] New Unity 2022 LTS project (3D, URP or Built-in — NOT HDRP)
- [ ] Switch platform to Universal Windows Platform (File > Build Settings)
- [ ] Import MRTK 2.8 via Mixed Reality Feature Tool:
  - Mixed Reality Toolkit Foundation
  - Mixed Reality OpenXR Plugin
- [ ] Run MRTK Project Configurator, apply recommended settings
- [ ] Add MRTK default scene objects (MixedRealityToolkit +
      MixedRealityPlayspace) via MRTK menu
- [ ] Project Settings > XR Plug-in Management > enable OpenXR, enable
      Microsoft HoloLens feature group
- [ ] Build (UWP, ARM64) → open generated .sln in Visual Studio → deploy
      to device (or use Holographic Remoting instead — faster loop, try
      this first)
- [ ] Confirm: put on headset, see the default MRTK cursor/rig, nothing
      crashes

**Checkpoint:** Blank MRTK app runs on the actual HoloLens without
errors. This is the single most important checkpoint — most toolchain
pain happens here, before any of your own code exists.

---

## Phase 2 — Backend Relay Skeleton (can be done in parallel with Phase 1)

- [ ] Set up Python environment on backend PC (`venv` recommended)
- [ ] Install: `websockets` (or `fastapi` + `uvicorn` with a WS route),
      SDK for your chosen first LLM provider (`anthropic`, `openai`, or
      `google-generativeai`)
- [ ] Write minimal WebSocket server:
  - Accepts a connection
  - On receiving `{"type": "prompt", "text": "..."}`, calls the LLM API
  - Sends back `{"type": "response", "text": "..."}`
- [ ] Test with a plain WebSocket client (e.g. `websocat`, a Python test
      script, or a browser console) — confirm round-trip works BEFORE
      touching Unity at all
- [ ] Note the backend PC's LAN IP and chosen port — HoloLens will need
      this

**Checkpoint:** From a terminal, you can send a text prompt over
WebSocket to your backend PC and get an LLM response back, with no
HoloLens involved yet.

---

## Phase 3 — Unity Client Talks to Backend (text only, no voice yet)

- [ ] Add `NativeWebSocket` (or equivalent) Unity package
- [ ] Write `BackendConnection.cs`: connects to backend WS URL on start,
      exposes `SendPrompt(string)` and an event/callback for responses
- [ ] Build one MRTK floating panel with `TextMeshPro` text field
- [ ] Temporary test trigger: MRTK button labeled "Test" that sends a
      hardcoded prompt string and displays the response text on the panel
- [ ] Deploy to device, press the button, confirm the panel updates with
      a real LLM response

**Checkpoint:** This IS Milestone 1 from the PRD, minus voice input.
Physically pressing a hologram button gets you a real Claude/GPT/Gemini
answer rendered as a hologram.

---

## Phase 4 — Voice In

- [ ] Choose approach:
  - **Option A (simpler first pass):** Windows built-in
    `SpeechRecognizer` API in Unity/UWP — transcribes on-device, send
    resulting text over the existing WebSocket connection (reuses all of
    Phase 3's plumbing)
  - **Option B (more flexible later):** stream raw audio to backend,
    transcribe with Whisper there — more setup, more control, needed if
    you want non-English support or better accuracy later
  - Recommendation: do Option A first since it's a smaller change on top
    of working Phase 3 code; swap to Option B in a later milestone if
    needed
- [ ] Add MRTK "press and hold to talk" or air-tap-to-start/air-tap-to-stop
      interaction wired to the speech recognizer
- [ ] Replace the Phase 3 test button with this voice flow
- [ ] Deploy, speak a question, confirm panel updates with the answer

**Checkpoint:** This is the full Milestone 1 success criteria from the
PRD — speak, see an answer, 10 times in a row reliably.

---

## Phase 5 — Voice Out (Milestone 2)

- [ ] Backend: add TTS step after LLM response (start with a cloud TTS
      API for quality, or Windows TTS for zero extra dependencies)
- [ ] Backend sends audio back to client — either as a URL to fetch or
      raw bytes over the WebSocket (base64-encoded is simplest to start)
- [ ] Unity: on receiving audio, play via `AudioSource`
- [ ] Add simple conversation history: backend keeps last N turns in
      memory per connection, includes them in each LLM call

**Checkpoint:** Full spoken back-and-forth loop, no screen/phone/laptop
needed once the headset is on.

---

## Phase 6 — Model-Agnostic Backend (Milestone 3)

- [ ] Refactor backend LLM call behind a small provider interface
      (`get_response(prompt, history) -> str`)
- [ ] Implement providers for Claude, GPT, Gemini behind that interface
- [ ] Config file (YAML/JSON/.env) selects active provider + API key,
      no code changes needed to switch
- [ ] (Optional, if pursuing Hermes Agent as backend instead of direct
      API calls) — replace the direct-LLM-call provider with a Hermes
      gateway client; Hermes already handles multi-provider routing, so
      this may subsume the provider-interface work entirely

**Checkpoint:** Can switch which LLM answers your questions by editing a
config file and restarting the backend — no Unity rebuild needed.

---

## Phase 7 — Spatial Polish (Milestone 4, optional/ongoing)

- [ ] Add MRTK `SolverHandler` + `Orbital` or `RadialView` solver so the
      panel follows gaze/hand naturally instead of being pinned in one spot
- [ ] Add a second panel (e.g. status/connection indicator) as a
      separate spatial object
- [ ] Add hand-tracked near/far interaction for dismiss/recall
- [ ] World-anchor the main panel so it stays put in a chosen room
      location across sessions (MRTK spatial anchor / Azure Spatial
      Anchors if cross-session persistence is wanted — optional, adds a
      cloud dependency)

---

## Phase 8 — Personality Layer (Milestone 5, optional, last)

- [ ] Visual pass: panel materials, entrance/exit animation, idle-state
      visual (e.g. subtle particle or glow when listening vs. thinking
      vs. speaking)
- [ ] Wake-word support (replaces press/air-tap-to-talk) if desired —
      note this likely requires Option B voice pipeline (Phase 4) for a
      always-listening local wake-word model, since constantly streaming
      to a cloud STT is wasteful/costly
- [ ] Optional: let the agent trigger richer panel content (images,
      simple charts) instead of text-only, mirroring the "media panel"
      pattern seen in prior browser-based Jarvis-style projects

---

## Suggested Order of Attack

Phases 0–3 are the critical path and should be done in order — everything
else can be reprioritized based on what's most fun/useful once the core
loop works. Do not skip the Phase 1 checkpoint (blank MRTK app on
device) — diagnosing toolchain issues is much harder once your own code
is mixed in.
