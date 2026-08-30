"""
HoloLens Jarvis — backend relay server.

Minimal WebSocket server that:
  1. Accepts a connection from the Unity/HoloLens client
  2. Receives {"type": "prompt", "text": "..."}
  3. Calls the configured LLM provider
  4. Sends back {"type": "response", "text": "..."}

This is the Phase 2 / Phase 3 skeleton from docs/BUILD_PLAN.md.
TTS, audio streaming, and multi-turn history are added in later phases —
see providers.py and BUILD_PLAN.md for what's stubbed vs. implemented.
"""

import asyncio
import json
import logging
from pathlib import Path

import websockets
import yaml

from providers import get_provider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("relay")

CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CONFIG_PATH}. Copy config.example.yaml to config.yaml "
            "and fill in your LLM provider + API key."
        )
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


async def handle_connection(websocket):
    config = load_config()
    provider = get_provider(config)
    log.info("Client connected. Using provider: %s", config.get("provider"))

    # Phase 5 will make this per-connection conversation history.
    history: list[dict] = []

    async for raw_message in websocket:
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            log.warning("Received non-JSON message, ignoring: %r", raw_message)
            continue

        if message.get("type") != "prompt":
            log.warning("Unknown message type: %r", message.get("type"))
            continue

        prompt_text = message.get("text", "")
        if not prompt_text.strip():
            continue

        log.info("Prompt: %s", prompt_text)

        try:
            response_text = await provider.get_response(prompt_text, history)
        except Exception as e:
            log.exception("Provider call failed")
            response_text = f"(backend error: {e})"

        history.append({"role": "user", "content": prompt_text})
        history.append({"role": "assistant", "content": response_text})

        await websocket.send(json.dumps({"type": "response", "text": response_text}))
        log.info("Response: %s", response_text)


async def main():
    config = load_config()
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8765)

    log.info("Starting relay server on %s:%s", host, port)
    async with websockets.serve(handle_connection, host, port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
