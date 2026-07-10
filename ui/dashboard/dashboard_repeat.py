from __future__ import annotations

import wx


class DashboardRepeat:

    INTERVAL = 50

    def __init__(self, dashboard):

        self.dashboard = dashboard

        self.timer = wx.Timer(dashboard)

        self._callback = None

        dashboard.Bind(
            wx.EVT_TIMER,
            self.on_timer,
            self.timer,
        )

    # --------------------------------------------------

    def start(self, callback):

        self._callback = callback

        if not self.timer.IsRunning():

            self.timer.Start(self.INTERVAL)

    # --------------------------------------------------

    def stop(self):

        if self.timer.IsRunning():

            self.timer.Stop()

        self._callback = None

    # --------------------------------------------------

    def on_timer(self, event):

        if self._callback is not None:

            self._callback()