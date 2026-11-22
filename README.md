# Wi-Fi Phone Touchpad & PC Remote

Turn your smartphone into a low-latency wireless touchpad, keyboard, and media remote for your PC over your local Wi-Fi network—with **zero mobile app installation** required.

## Project Overview

**Wi-Fi Phone Touchpad** is a lightweight, cross-platform remote control solution built with **Python (`aiohttp`, `pynput`)** and **HTML5/WebSockets**. Your PC runs a tiny local web server and generates a QR code; scanning it from any smartphone browser opens a responsive, dark-mode multi-touch trackpad that communicates with your computer in real time.

### Key Features

* **Multi-Touch Trackpad:** Smooth 1-finger cursor tracking with acceleration, tap-to-click, double-tap, 2-finger right-click, and 2-finger natural scrolling.

* **Drag Lock Mode:** Dedicated toggle to hold down left-click for effortless drag-and-drop.

* **Wireless Keyboard & Shortcuts:** Type text straight from your phone to your PC, plus one-tap hotkeys (`Copy`, `Paste`, `Undo`, `Alt+Tab`, `Esc`, `Tab`, `Enter`).

* **Media & Navigation Deck:** Control system volume, mute, play/pause, arrow keys, and the `Win/Cmd` key from across the room.

* **PWA & Security Ready:** Supports **Add to Home Screen** on iOS and Android for a full-screen native app feel, keeps your screen awake while in use, and includes optional `--pin` protection.

## Step-by-Step Setup & How to Use

### Step 1: Download the Project Files

Download or clone the repository onto your PC and make sure these three files are in the **same folder**:

* `pc_server.py`

* `index.html`

* `requirements.txt`

### Step 2: Install Python (If Not Installed)

1. Download Python 3.10 or newer from [python.org/downloads](https://www.python.org/downloads/).

2. Run the installer (**Windows users:** check **"Add python.exe to PATH"** at the bottom before clicking *Install Now*).

### Step 3: Install Required Python Libraries

Open a terminal or Command Prompt inside your project folder and run:

```
pip install -r requirements.txt

```

*(On Windows, if `pip` is not recognized, run `python -m pip install -r requirements.txt` instead.)*

### Step 4: Start the Server on Your PC

Start the server from the same terminal window:

```
python pc_server.py

```

**Optional command-line flags:**

* Require a 4-digit security PIN: `python pc_server.py --pin 1234`

* Use a custom network port: `python pc_server.py --port 9000`

A local URL (e.g., `http://192.168.1.15:8080`) and a **QR code** will appear in your terminal. Leave this terminal window open while using the touchpad.

### Step 5: Connect Your Phone

1. Ensure both your **PC and phone are connected to the same Wi-Fi network**.

2. Scan the QR code displayed in your terminal using your phone's camera (or open Chrome/Safari on your phone and enter the `http://<PC-IP>:8080` address).

3. *(Optional)* Tap **Share / Menu -> Add to Home Screen** in your mobile browser to launch it like a standalone app.

## Gesture & Control Reference\`

| Gesture / Button | Action on PC | 
| ----- | ----- | 
| **1-Finger Drag** | Move mouse cursor | 
| **1-Finger Tap** | Left click | 
| **1-Finger Double-Tap** | Double click | 
| **2-Finger Tap** | Right click | 
| **2-Finger Drag** | Scroll vertically or horizontally | 
| **Drag Button** | Toggles left mouse button hold for dragging | 
| **Keyboard Tab** | Type text & send shortcuts (`Copy`, `Paste`, `Undo`, `Alt+Tab`) | 
| **Media / Nav Tab** | Volume Up/Down, Mute, Play/Pause, Arrow keys, `Win/Cmd` | 
| **Settings Button** | Adjust pointer sensitivity, scroll speed, haptics, and wake lock | 
