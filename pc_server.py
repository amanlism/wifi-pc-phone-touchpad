#!/usr/bin/env python3
"""
Wi-Fi Touchpad & Remote Control Server for PC
Serves the mobile touchpad web app and handles real-time WebSocket input
to control the PC mouse, keyboard, and media keys.
"""

import argparse
import asyncio
import json
import os
import socket
import sys
from pathlib import Path

from aiohttp import web, WSMsgType
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Button, Controller as MouseController

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

mouse = MouseController()
keyboard = KeyboardController()

# Accumulate fractional mouse movements for smooth low-speed tracking
frac_x = 0.0
frac_y = 0.0

SPECIAL_KEYS = {
    "enter": Key.enter,
    "backspace": Key.backspace,
    "tab": Key.tab,
    "esc": Key.esc,
    "space": Key.space,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right,
    "delete": Key.delete,
    "home": Key.home,
    "end": Key.end,
    "page_up": Key.page_up,
    "page_down": Key.page_down,
    "win": Key.cmd,
    "cmd": Key.cmd,
    "ctrl": Key.ctrl,
    "alt": Key.alt,
    "shift": Key.shift,
    "volume_up": Key.media_volume_up,
    "volume_down": Key.media_volume_down,
    "mute": Key.media_volume_mute,
    "play_pause": Key.media_play_pause,
    "next": Key.media_next,
    "prev": Key.media_previous,
}

MOUSE_BUTTONS = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}


def get_lan_ip() -> str:
    """Detect the PC's active local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually send packets; finds the outbound interface IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def handle_input_event(data: dict) -> None:
    """Execute a mouse, scroll, or keyboard event on the PC."""
    global frac_x, frac_y
    event_type = data.get("type")

    if event_type == "move":
        dx = float(data.get("dx", 0)) + frac_x
        dy = float(data.get("dy", 0)) + frac_y
        move_x = int(dx)
        move_y = int(dy)
        frac_x = dx - move_x
        frac_y = dy - move_y
        if move_x != 0 or move_y != 0:
            mouse.move(move_x, move_y)

    elif event_type == "click":
        btn = MOUSE_BUTTONS.get(data.get("button", "left"), Button.left)
        action = data.get("action", "tap")
        if action == "tap":
            mouse.click(btn, 1)
        elif action == "double":
            mouse.click(btn, 2)
        elif action == "down":
            mouse.press(btn)
        elif action == "up":
            mouse.release(btn)

    elif event_type == "scroll":
        dx = int(round(float(data.get("dx", 0))))
        dy = int(round(float(data.get("dy", 0))))
        if dx != 0 or dy != 0:
            mouse.scroll(dx, dy)

    elif event_type == "text":
        text = data.get("text", "")
        if text:
            keyboard.type(text)

    elif event_type == "key":
        key_name = str(data.get("key", "")).lower()
        key_obj = SPECIAL_KEYS.get(key_name)
        if key_obj is not None:
            keyboard.press(key_obj)
            keyboard.release(key_obj)
        elif len(key_name) == 1:
            keyboard.press(key_name)
            keyboard.release(key_name)

    elif event_type == "hotkey":
        keys = data.get("keys", [])
        resolved = []
        for k in keys:
            k_low = str(k).lower()
            if k_low == "ctrl_or_cmd":
                resolved.append(Key.cmd if sys.platform == "darwin" else Key.ctrl)
            elif k_low in SPECIAL_KEYS:
                resolved.append(SPECIAL_KEYS[k_low])
            elif len(k_low) == 1:
                resolved.append(k_low)
        for k in resolved:
            keyboard.press(k)
        for k in reversed(resolved):
            keyboard.release(k)


async def index_handler(request: web.Request) -> web.Response:
    """Serve the mobile touchpad web app."""
    if not INDEX_FILE.exists():
        return web.Response(
            text="index.html not found next to pc_server.py", status=404
        )
    return web.FileResponse(INDEX_FILE)


async def manifest_handler(request: web.Request) -> web.Response:
    """Serve a PWA manifest so users can Add to Home Screen on iOS/Android."""
    manifest = {
        "name": "PC Touchpad",
        "short_name": "Touchpad",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a",
        "orientation": "portrait",
    }
    return web.json_response(manifest)


async def ws_handler(request: web.Request) -> web.WebSocketResponse:
    """Handle WebSocket connections from the phone."""
    ws = web.WebSocketResponse(heartbeat=20.0)
    await ws.prepare(request)

    required_pin = request.app.get("pin")
    authenticated = required_pin is None

    peer = request.remote
    print(f"[+] Phone connected from {peer}")

    await ws.send_json({"type": "auth_required", "required": not authenticated})

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                except json.JSONDecodeError:
                    continue

                if not authenticated:
                    if data.get("type") == "auth" and str(data.get("pin", "")) == required_pin:
                        authenticated = True
                        await ws.send_json({"type": "auth_ok"})
                    else:
                        await ws.send_json({"type": "auth_fail"})
                    continue

                handle_input_event(data)

            elif msg.type == WSMsgType.ERROR:
                print(f"[!] WebSocket error: {ws.exception()}")
    finally:
        print(f"[-] Phone disconnected ({peer})")

    return ws


def print_banner(url: str, pin: str | None) -> None:
    print("\n" + "=" * 54)
    print("  PC TOUCHPAD SERVER RUNNING")
    print("=" * 54)
    print(f"  Open on your phone:  {url}")
    if pin:
        print(f"  Access PIN:          {pin}")
    print("  Press Ctrl+C to stop.")
    print("=" * 54 + "\n")

    if HAS_QRCODE:
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Wi-Fi Phone Touchpad Server for PC")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--pin", default=None, help="Optional 4-digit PIN for security")
    args = parser.parse_args()

    app = web.Application()
    app["pin"] = args.pin
    app.router.add_get("/", index_handler)
    app.router.add_get("/manifest.json", manifest_handler)
    app.router.add_get("/ws", ws_handler)

    lan_ip = get_lan_ip()
    url = f"http://{lan_ip}:{args.port}"
    print_banner(url, args.pin)

    web.run_app(app, host=args.host, port=args.port, print=None)


if __name__ == "__main__":
    main()