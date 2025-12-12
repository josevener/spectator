# core/streamer.py
from PIL import Image
import pyautogui
import io
import base64
import hashlib
from .utils import log

class ScreenStreamer:
    def __init__(self, quality=70, enable_diff=True):
        self.quality = quality
        self.enable_diff = enable_diff
        self.last_hash = None

    def capture(self):
        try:
            screenshot = pyautogui.screenshot()
            img = screenshot.resize((1280, 720), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="WEBP", quality=self.quality, method=6)
            img_bytes = buffer.getvalue()
            current_hash = hashlib.md5(img_bytes).digest()

            if self.enable_diff and self.last_hash == current_hash:
                return None

            self.last_hash = current_hash
            b64 = base64.b64encode(img_bytes).decode()
            result = f"data:image/webp;base64,{b64}"
            print(f"Screenshot captured: {len(result)} chars")
            
            return f"data:image/webp;base64,{b64}"
        except Exception as e:
            log.error(f"Screenshot failed: {e}")
            return None