from __future__ import annotations

import wx


class DashboardTimer:

    FPS = 60

    def __init__(self, dashboard):

        self.dashboard = dashboard

        self.timer = wx.Timer(dashboard)

        dashboard.Bind(
            wx.EVT_TIMER,
            self.on_timer,
            self.timer,
        )

        self.timer.Start(
            int(1000 / self.FPS)
        )

    # --------------------------------------------------

    def on_timer(self, event):

        self.dashboard.update()

    # --------------------------------------------------

    def stop(self):

        if self.timer.IsRunning():
            self.timer.Stop()