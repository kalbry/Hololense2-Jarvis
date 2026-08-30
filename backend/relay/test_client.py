"""
Standalone test client — confirms the backend relay works BEFORE touching
Unity at all. This is the Phase 2 checkpoint from docs/BUILD_PLAN.md.

Usage:
    python test_client.py
    python test_client.py --host 192.168.1.50 --port 8765
"""

import argparse
import asyncio
import json

import websockets


async def run(host: str, port: int):
    uri = f"ws://{host}:{port}"
    print(f"Connecting to {uri} ...")
    async with websockets.connect(uri) as websocket:
        print("Connected. Type a prompt and press enter (Ctrl+C to quit).\n")
        while True:
            prompt = input("> ")
            if not prompt.strip():
                continue
            await websocket.send(json.dumps({"type": "prompt", "text": prompt}))
            raw_response = await websocket.recv()
            response = json.loads(raw_response)
            print(f"\n{response.get('text')}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    try:
        asyncio.run(run(args.host, args.port))
    except KeyboardInterrupt:
        print("\nBye.")
