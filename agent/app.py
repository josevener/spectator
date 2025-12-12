# app.py
import wx
import sys
from pathlib import Path
from core.utils import load_config, log
from ui.tray import TrayIcon

if __name__ == "__main__":
    if "--silent" in sys.argv:
        # Headless mode
        from core.agent import Agent
        config = load_config()
        config.update({
            "url": config.get("server_wss") or config.get("server_url", "ws://localhost:5500/ws/agent"),
            "agent_name": config.get("agent_name", f"PC-{__import__('os').getenv('COMPUTERNAME')}"),
            "secret_key": config["secret_key"]
        })
        Agent(config).start()
        while True: __import__('time').sleep(100)
    else:
        app = wx.App(False)
        config = load_config()
        config.update({
            "url": config.get("server_wss") or config.get("server_url", "ws://localhost:5500/ws/agent"),
            "agent_name": config.get("agent_name", f"PC-{__import__('os').getenv('COMPUTERNAME')}"),
            "secret_key": config["secret_key"],
            "capture_fps": config.get("capture_fps", 3),
            "screen_quality": config.get("screen_quality", 70),
            "enable_diff": config.get("enable_diff", True)
        })
        TrayIcon(config)
        app.MainLoop()