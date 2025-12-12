# core/agent.py
import websocket
import threading
import time
import json
import psutil                  # ← THIS WAS MISSING!
from .streamer import ScreenStreamer
from .utils import log

try:
    import win32gui
    def get_active_window():
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return "Desktop"
        title = win32gui.GetWindowText(hwnd)
        return title.strip() or "Unknown App"
except ImportError:
    def get_active_window():
        return "Desktop"


class Agent:
    def __init__(self, config, on_status_change=None):
        self.config = config
        self.on_status = on_status_change or (lambda c, f: None)
        self.connected = False
        self.running = True

        self.streamer = ScreenStreamer(
            quality=config.get("screen_quality", 70),
            enable_diff=config.get("enable_diff", True)
        )
        self.fps = config.get("capture_fps", 3)

        self.connect()

    def connect(self):
        url = f"{self.config['url']}?secret_key={self.config['secret_key']}"
        log.info(f"Connecting to {url}")

        self.ws = websocket.WebSocketApp(
            url,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.on_message
        )
        threading.Thread(
            target=self.ws.run_forever,
            kwargs={"ping_interval": 15},
            daemon=True
        ).start()

    def on_open(self, ws):
        log.info("WebSocket connected")
        self.connected = True
        # Pass actual FPS from config
        self.on_status(True, self.fps)

    def on_close(self, *args):
        log.warning("Disconnected → reconnecting...")
        self.connected = False
        self.on_status(False, 0)
        if self.running:
            time.sleep(5)
            self.connect()

    def on_error(self, ws, err):
        log.error(f"WS Error: {err}")

    def on_message(self, ws, msg):
        pass  # you can handle welcome/pong here later

    def send_frame(self):
        if not self.connected:
            return

        screenshot = self.streamer.capture()
        
        # THIS IS CRITICAL — must include "screenshot" key with full data URL
        payload = {
            "screenshot": screenshot or None,  # Must be the full "data:image/webp;base64,..."
            "stats": {
                "cpu": round(psutil.cpu_percent(), 1),
                "ram_percent": round(psutil.virtual_memory().percent, 1),
                "ram_gb": round(psutil.virtual_memory().used / 1024**3, 1),
                "active_window": get_active_window(),
                "uptime": int(time.time() - psutil.boot_time())
            },
            "agent_name": self.config["agent_name"]
        }

        try:
            self.ws.send(json.dumps(payload))
            print("Sent frame with screenshot:", bool(screenshot))  # ← DEBUG LINE
        except Exception as e:
            print("Send failed:", e)

    def start(self):
        def loop():
            while self.running:
                self.send_frame()
                time.sleep(1 / self.fps)
        threading.Thread(target=loop, daemon=True).start()

    def stop(self):
        self.running = False
        if hasattr(self, "ws"):
            self.ws.close()