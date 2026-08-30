# unity-client

This folder holds source (scripts) for the HoloLens 2 Unity project.
Unity project binary/generated folders (`Library/`, `Temp/`, `Build/`,
`.vs/`, etc.) are intentionally not committed — see root `.gitignore`.

## Setting up the actual Unity project

This repo does not include a full generated Unity project (those are
mostly binary/cache files that shouldn't be in git). To set it up:

1. Open Unity Hub, create a new **3D (URP or Built-in)** project on
   **Unity 2022 LTS** — see `docs/BUILD_PLAN.md` Phase 0–1 for exact
   version guidance.
2. Point the new project's `Assets/Scripts` folder at (or copy in) the
   `.cs` files from this repo's `unity-client/Assets/Scripts/`.
3. Follow `docs/BUILD_PLAN.md` Phase 1 to install MRTK 2.8 and configure
   the project for HoloLens 2 / UWP / OpenXR.
4. Install the `NativeWebSocket` package (Package Manager → Add package
   from git URL → `https://github.com/endel/NativeWebSocket.git#upm`).
5. Build the scene per Phase 3: an MRTK floating panel with a
   `TextMeshPro` text field, a `BackendConnection` object with
   `BackendConnection.cs` attached (set `backendHost`/`backendPort` in
   the Inspector), and `ResponsePanelController.cs` wired to both.

## Scripts in this repo

| File | Purpose |
|---|---|
| `Scripts/BackendConnection.cs` | WebSocket client — connects to the Python backend relay, sends prompts, receives responses |
| `Scripts/ResponsePanelController.cs` | Displays backend responses on the MRTK panel's TextMeshPro text |

Once you have real prefabs/scenes built, commit them here — Unity scene
(`.unity`) and prefab (`.prefab`) files are text-based YAML and diff
reasonably well in git, unlike `Library/`.
