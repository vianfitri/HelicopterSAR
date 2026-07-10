from __future__ import annotations

import wx


class DashboardKeyboard:

    STEP = 0.10

    def __init__(self, dashboard):

        self.dashboard = dashboard

        dashboard.Bind(
            wx.EVT_CHAR_HOOK,
            self.on_key,
        )

    # --------------------------------------------------

    def on_key(self, event):

        controller = self.dashboard.controller

        key = event.GetKeyCode()

        if key == wx.WXK_LEFT:

            controller.set_track_position(
                controller.track_position - self.STEP
            )

            self.dashboard.transversal.slider.set_value(
                controller.track_position
            )

            return

        if key == wx.WXK_RIGHT:

            controller.set_track_position(
                controller.track_position + self.STEP
            )

            self.dashboard.transversal.slider.set_value(
                controller.track_position
            )

            return

        if key == wx.WXK_UP:

            controller.set_hoist_length(
                controller.hoist_length - self.STEP
            )

            self.dashboard.hoist_control.slider.set_value(
                controller.hoist_length
            )

            return

        if key == wx.WXK_DOWN:

            controller.set_hoist_length(
                controller.hoist_length + self.STEP
            )

            self.dashboard.hoist_control.slider.set_value(
                controller.hoist_length
            )

            return

        event.Skip()