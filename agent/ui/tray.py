# ui/tray.py
import wx
import wx.adv
from pathlib import Path
from core.agent import Agent
from .panel import StatusPanel

class TrayIcon(wx.adv.TaskBarIcon):
    def __init__(self, config):
        super().__init__()
        self.icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
        icon = wx.Icon(str(self.icon_path)) if self.icon_path.exists() else wx.ArtProvider.GetIcon(wx.ART_INFORMATION)
        self.SetIcon(icon, "Cafe Spectator")

        self.panel = StatusPanel()
        self.agent = Agent(config, on_status_change=self.panel.update_status)
        self.agent.start()

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.toggle_panel)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, "Show/Hide Window")
        menu.AppendSeparator()
        menu.Append(2, "Exit")
        self.Bind(wx.EVT_MENU, self.on_menu)
        return menu

    def on_menu(self, event):
        if event.GetId() == 1:
            self.toggle_panel()
        else:
            self.agent.stop()
            self.panel.Close()
            self.RemoveIcon()
            wx.CallAfter(wx.GetApp().ExitMainLoop)

    def toggle_panel(self, event=None):
        self.panel.Show(not self.panel.IsShown())
        if self.panel.IsShown():
            self.panel.Raise()