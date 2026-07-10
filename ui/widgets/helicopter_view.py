from __future__ import annotations

import wx

from ui.base.base_panel import BasePanel


class HelicopterView(BasePanel):

    def __init__(
        self,
        parent,
        **kwargs,
    ):

        self._track_position = 5.0
        self._hoist_length = 5.0

        super().__init__(
            parent,
            **kwargs,
        )

    # --------------------------------------------------

    def set_track_position(self, value: float):

        self._track_position = value
        self.Refresh(False)

    # --------------------------------------------------

    def set_hoist_length(self, value: float):

        self._hoist_length = value
        self.Refresh(False)

    # --------------------------------------------------

    def draw_foreground(self, gc):

        w, h = self.GetClientSize()

        margin = 40

        #
        # helicopter position
        #

        x = margin + (
            (w - margin * 2)
            * self._track_position
            / 10.0
        )

        y = 60

        #
        # cable
        #

        cable = (
            h * 0.6
            * self._hoist_length
            / 10.0
        )

        gc.SetPen(
            wx.Pen(
                self.palette.text,
                2,
            )
        )

        gc.StrokeLine(
            x,
            y,
            x,
            y + cable,
        )

        #
        # helicopter
        #

        gc.SetBrush(
            wx.Brush(
                self.palette.primary
            )
        )

        gc.SetPen(
            wx.Pen(
                self.palette.border,
                1,
            )
        )

        gc.DrawRoundedRectangle(
            x - 35,
            y - 12,
            70,
            24,
            6,
        )

        gc.StrokeLine(
            x - 50,
            y - 18,
            x + 50,
            y - 18,
        )

        gc.StrokeLine(
            x - 45,
            y + 15,
            x - 20,
            y + 30,
        )

        gc.StrokeLine(
            x + 45,
            y + 15,
            x + 20,
            y + 30,
        )

        #
        # hook
        #

        gc.SetBrush(
            wx.Brush(
                self.palette.warning
            )
        )

        gc.DrawEllipse(
            x - 6,
            y + cable - 6,
            12,
            12,
        )