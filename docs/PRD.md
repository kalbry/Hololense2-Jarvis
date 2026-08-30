# PRD — HoloLens Jarvis (working title)

## 1. Summary

A personal, holographic AI assistant running on Microsoft HoloLens 2, driven
by a cloud or local LLM (Claude, GPT, Gemini, or a self-hosted agent like
Hermes) via a LAN-based backend relay. The HoloLens acts as a thin
spatial-computing client: voice in, holographic panels out. All reasoning,
memory, and tool use happen on a backend PC on the same network.

This is a personal side project, single-user, not intended for distribution
or commercial use. Scope is deliberately small: prove the pipeline works
end-to-end before adding polish.

## 2. Problem / Motivation

- Owner has an unused HoloLens 2 (Microsoft has de-emphasized new HoloLens
  hardware, but the device is fully capable and still supported for
  development with pinned tooling).
- Existing "AI + smart glasses" hobbyist projects (Even Realities G2, Meta
  Ray-Ban Display) are 2D HUD overlays at best — none offer true stereo
  holographic rendering.
- HoloLens 2 is the only owned device capable of real spatially-anchored,
  both-eyes holographic UI, which is a categorically different (better)
  experience than a flat lens overlay.
- Goal: turn "unused hardware" into "personal Jarvis" — voice-driven,
  visually present, useful for glanceable info and hands-free agent
  interaction.

## 3. Goals

1. Speak a question or command; get a spoken and visual response rendered
   as a holographic panel anchored in space.
2. Backend is model-agnostic: swap between Claude, GPT, Gemini, or a
   self-hosted Hermes Agent via config, not code changes.
3. Runs entirely on owner's own hardware/network — no third-party cloud
   relay service required (LLM API calls themselves are the only external
   dependency, same as any chat client).
4. Establish a working skeleton fast (Milestone 1), then layer on
   polish (multiple panels, gesture control, persistent memory, tool use)
   incrementally.

## 4. Non-Goals (explicitly out of scope for v1)

- Not a commercial product, not for distribution, not multi-user.
- Not attempting full Iron-Man cinematic UI on day one — that is a later
  milestone, not a launch requirement.
- Not building custom on-device ML — STT/LLM inference happens on the
  backend, not on the HoloLens itself (HoloLens 2 hardware is not suited
  to running modern LLMs locally).
- Not targeting HoloLens (1st gen) — HoloLens 2 only.
- No app store submission / no Microsoft Store distribution.

## 5. Target Hardware & Toolchain (pinned — do not deviate without reason)

HoloLens 2 dropped support in new Unity/Unity OpenXR releases as of
June 23, 2025. Using current-year default installs of Unity will NOT work
for this device. Use exactly:

| Component                  | Required version                          |
|-----------------------------|--------------------------------------------|
| Unity Editor                | 2022 LTS (last HoloLens-2-supporting build) |
| MRTK                        | MRTK 2.8 (NOT MRTK3 — Microsoft's own current guidance recommends 2.8 for HoloLens 2 despite MRTK3 being newer) |
| XR pipeline                 | OpenXR (Unity OpenXR Plugin, HoloLens-2-supporting version) |
| Build target                | Universal Windows Platform (UWP), ARM64 |
| Iteration method             | Holographic Remoting (live-stream from Editor to headset — avoids full compile+deploy loop during development) |

Backend runs on any always-on PC on the same LAN (Windows, Mac, or Linux —
language-agnostic relay).

## 6. High-Level Architecture

```
 ┌────────────────────────┐        LAN (WebSocket/HTTP)       ┌───────────────────────────┐
 │      HoloLens 2         │ ───────────────────────────────► │       Backend PC           │
 │  (Unity + MRTK client)  │ ◄─────────────────────────────── │   (relay + agent runtime)  │
 │                          │                                  │                            │
 │  - Mic capture           │                                  │  - STT (Whisper, local     │
 │  - Spatial UI (panels)   │                                  │    or cloud)               │
 │  - TTS playback           │                                 │  - LLM call (Claude/GPT/   │
 │  - Voice/gesture input    │                                 │    Gemini/Hermes)          │
 │                          │                                  │  - TTS generation           │
 └────────────────────────┘                                  │  - (later) tool use, memory │
                                                                └───────────────────────────┘
```

Data flow per turn:
1. User speaks → HoloLens streams audio (or on-device Windows Speech
   Platform transcribes locally, sends text) to backend.
2. Backend relay transcribes (if not already text) → sends prompt to
   configured LLM provider.
3. LLM response text returned → backend optionally generates TTS audio.
4. Backend sends `{text, audio_url_or_bytes}` back to HoloLens over the
   open WebSocket.
5. Unity client renders text in a spatial panel and plays audio.

## 7. Milestones

### Milestone 1 — "Hello Hologram" (proof of pipeline)
- Single floating text panel in front of the user on app launch.
- Press-and-hold (or "select") voice input, using built-in Windows Speech
  recognition OR streamed audio to backend Whisper — pick whichever is
  faster to stand up first.
- Backend relay: minimal script, single LLM provider hardcoded (start
  with whichever of Claude/GPT/Gemini the owner already has an API key
  for), returns text only (no TTS yet).
- Success criteria: speak a question, see the answer appear as text in
  the panel, within a few seconds, reliably, 10 times in a row.

### Milestone 2 — Voice out
- Add TTS (start simple — Windows built-in TTS or a cloud TTS API) so
  responses are spoken, not just displayed.
- Add basic conversation history (last N turns) sent as context each call.

### Milestone 3 — Model-agnostic backend
- Config-driven provider switch (Claude / GPT / Gemini / self-hosted
  Hermes Agent) without code changes — a config file or env var selects
  provider.
- If using Hermes Agent as backend: relay becomes a thin bridge between
  HoloLens WebSocket and Hermes's own gateway/API instead of calling an
  LLM API directly.

### Milestone 4 — Spatial polish
- Multiple panels (e.g. separate "conversation" panel and "status/info"
  panel).
- Panels anchored in world space (stay put when you look away and back),
  using MRTK spatial anchor components.
- Hand-tracking based dismiss/recall gestures via MRTK.

### Milestone 5 — Personality / cinematic layer (optional, last)
- Visual theme pass (color, animation-in/animation-out for panels,
  "boot sequence," idle state indicator).
- Wake-word support instead of press-to-talk, if desired.
- Optional: agent-driven panel content (e.g. agent decides to show a
  chart or image, not just text) — mirrors the "media panels" pattern
  from prior art (jarvis_ai project referenced during research).

## 8. Backend Relay — Requirements

- Language: Python (recommended — fastest path to Whisper/TTS/LLM SDKs;
  not a hard requirement).
- Must run as a long-lived local service (systemd unit / Windows service /
  just a terminal window during development — start with the latter).
- WebSocket server (simplest real-time option for streaming text/audio
  both directions).
- Config file (not hardcoded secrets) for:
  - LLM provider selection + API key
  - STT method (local Whisper vs cloud)
  - TTS method (local vs cloud, voice selection)
- No requirement for a database or persistent memory in v1 — conversation
  history can be in-memory per session to start. Persistent memory is a
  post-v1 nice-to-have, not urgent given a single user.

## 9. Unity Client — Requirements

- MRTK 2.8 scene with:
  - One `ObjectManipulator` + `Follow` solver panel (a floating text
    panel that can be repositioned)
  - `TextMeshPro` for panel text rendering
  - Microphone capture via Unity's `Microphone` class or Windows
    `Windows.Media.SpeechRecognition` APIs
  - `UnityWebRequest` or a WebSocket client library (e.g.
    `NativeWebSocket` package) for backend communication
- No custom shaders / no HDRP (MRTK does not support HDRP — confirmed;
  use Built-in or URP pipeline only)

## 10. Risks / Known Constraints

- **Toolchain fragility**: HoloLens 2 Unity support is frozen at old
  versions. Any tutorial/blog post from after mid-2025 assuming "just use
  latest Unity" is wrong for this device — always cross-check against
  Microsoft Learn's current HoloLens 2 docs, not general Unity docs.
- **Battery/thermal**: HoloLens 2 has a limited battery life; long dev/test
  sessions on-device will need charging breaks or wired power.
- **Network dependency**: no backend reachable = no assistant. This is a
  LAN-tethered device experience, not a truly mobile one, unless a VPN
  or tunnel is set up later for off-LAN use.
- **Voice recognition in noisy environments**: HoloLens 2's mic array is
  good but not magic — test in the actual intended use environment early.

## 11. Success Definition (v1 / Milestone 1–3 complete)

Owner can put on the HoloLens, speak a question, and receive a spoken +
visually displayed answer from their LLM of choice, reliably, with no
laptop/phone in hand — the holographic panel is the entire interface.
