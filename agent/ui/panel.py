# ui/panel.py — FINAL PERFECT VERSION (ALL PERFORMANCE STATS VISIBLE)
import wx
import psutil
import time
import os
import GPUtil  # pip install gputil   ← for GPU usage

class StatusPanel(wx.Frame):
    def __init__(self):
        super().__init__(
            None,
            title="Spectator Agent",
            size=(560, 420),  # Tall enough for all info
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        )

        # Icon
        tray = getattr(wx.GetApp(), 'tray', None)
        if tray and hasattr(tray, 'icon_path') and tray.icon_path.exists():
            self.SetIcon(wx.Icon(str(tray.icon_path)))

        self.SetBackgroundColour(wx.Colour(250, 252, 255))
        self.Center()

        main_panel = wx.Panel(self)
        main_box = wx.BoxSizer(wx.VERTICAL)

        # === HEADER ===
        header = wx.Panel(main_panel)
        header.SetBackgroundColour(wx.Colour(10, 95, 190))
        header.SetMinSize((-1, 60))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(header, label="Cafe Spectator Agent")
        title.SetFont(wx.Font(18, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(wx.WHITE)
        hbox.AddStretchSpacer()
        hbox.Add(title, 0, wx.ALL, 20)
        hbox.AddStretchSpacer()
        header.SetSizer(hbox)

        # === GRID (11 rows) ===
        content = wx.Panel(main_panel)
        grid = wx.FlexGridSizer(rows=11, cols=2, vgap=12, hgap=25)
        grid.AddGrowableCol(1, 1)

        labels = [
            "Status", "Desktop", "Uptime", "Network", "CPU Usage",
            "RAM Usage", "Disk Usage", "GPU Usage", "GPU Temp", "WiFi Signal", "Streaming"
        ]
        self.values = []

        bold = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD)
        normal = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_NORMAL)

        for label in labels:
            lbl = wx.StaticText(content, label=label + ":")
            lbl.SetFont(bold)
            lbl.SetForegroundColour(wx.Colour(40, 40, 60))
            grid.Add(lbl, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

            val = wx.StaticText(content, label="Loading...")
            val.SetFont(normal)
            val.SetForegroundColour(wx.Colour(20, 20, 40))
            grid.Add(val, 1, wx.EXPAND)
            self.values.append(val)

        content.SetSizer(grid)

        # === FOOTER ===
        footer = wx.StaticText(main_panel, label="Right-click tray icon to exit • Monitoring Active")
        footer.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        footer.SetForegroundColour(wx.Colour(100, 100, 100))

        # === LAYOUT ===
        main_box.Add(header, 0, wx.EXPAND)
        main_box.Add(content, 1, wx.ALL | wx.EXPAND, 30)
        main_box.Add(footer, 0, wx.ALL | wx.CENTER, 18)
        main_panel.SetSizer(main_box)

        self.Show()

        # === LIVE UPDATER ===
        self.last_net = psutil.net_io_counters()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_all_stats, self.timer)
        self.timer.Start(1000)

    def get_gpu_info(self):
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return f"{gpu.load*100:.1f}%", f"{gpu.temperature:.0f}°C"
            return "No GPU", "—"
        except:
            return "Not detected", "—"

    def get_wifi_signal(self):
        try:
            import subprocess
            result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
            for line in result.splitlines():
                if "Signal" in line:
                    return line.split(":")[1].strip()
            return "Unknown"
        except:
            return "Not connected"

    def update_all_stats(self, event=None):
        # Network
        net = psutil.net_io_counters()
        up = (net.bytes_sent - self.last_net.bytes_sent) // 1024
        down = (net.bytes_recv - self.last_net.bytes_recv) // 1024
        self.last_net = net

        # Uptime
        uptime = int(time.time() - psutil.boot_time())
        h, r = divmod(uptime, 3600)
        m, _ = divmod(r, 60)

        # Disk
        disk = psutil.disk_usage('C:\\')
        disk_percent = disk.percent
        disk_used = disk.used // (1024**3)
        disk_total = disk.total // (1024**3)

        # GPU
        gpu_usage, gpu_temp = self.get_gpu_info()

        # WiFi
        wifi = self.get_wifi_signal()

        # Update all fields
        data = [
            "LIVE • Connected",                                           # 0 - Status (updated by agent)
            os.getenv('COMPUTERNAME', 'PC-01'),
            f"{h}h {m}m",
            f"Up: {up:,} KB/s   Down: {down:,} KB/s",
            f"{psutil.cpu_percent():.1f}%",
            f"{psutil.virtual_memory().percent:.1f}% ({psutil.virtual_memory().used//(1024**3):,} GB)",
            f"{disk_percent:.1f}% ({disk_used}/{disk_total} GB)",
            gpu_usage,
            gpu_temp,
            wifi,
            "3 FPS • WEBP • Smart Diff"
        ]

        for i in range(1, len(data)):
            self.values[i].SetLabel(data[i])

    def update_status(self, connected: bool, fps: int):
        status = "LIVE • Connected" if connected else "OFFLINE • Reconnecting..."
        color = wx.Colour(0, 160, 0) if connected else wx.Colour(220, 30, 30)
        self.values[0].SetLabel(f"{status} • {fps} FPS")
        self.values[0].SetForegroundColour(color)
        self.values[10].SetLabel(f"{fps} FPS • WEBP • Smart Diff")