from __future__ import annotations

import wx

from ui.base.base_widget import BaseWidget


class HoistView(BaseWidget):

    TOP_MARGIN = 24
    BOTTOM_MARGIN = 24

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        minimum: float = 0.0,
        maximum: float = 10.0,
        value: float = 5.0,
        **kwargs,
    ):

        self._minimum = minimum
        self._maximum = maximum
        self._length = value

        super().__init__(
            parent,
            id=id,
            **kwargs,
        )

        self.initialize()

    # ------------------------------------------------------

    def initialize(self):

        self.SetMinSize(
            (
                self.dip(180),
                self.dip(420),
            )
        )

    # ------------------------------------------------------

    @property
    def value(self):

        return self._length

    # ------------------------------------------------------

    def set_value(self, value: float):

        value = max(
            self._minimum,
            min(self._maximum, value)
        )

        if value == self._length:
            return

        self._length = value

        self.Refresh()

    # ------------------------------------------------------

    def draw(self, gc: wx.GraphicsContext):

        palette = self.palette

        w, h = self.GetClientSize()

        top = self.dip(self.TOP_MARGIN)
        bottom = h - self.dip(self.BOTTOM_MARGIN)

        #
        # Scale
        #

        gc.SetPen(
            wx.Pen(
                palette.graph_axis,
                2,
            )
        )

        x = w / 2

        gc.StrokeLine(
            x,
            top,
            x,
            bottom,
        )

        #
        # Labels
        #

        gc.SetFont(
            self.typography.body(),
            palette.text_secondary,
        )

        gc.DrawText(
            f"{self._minimum:.0f} m",
            x + self.dip(12),
            top - self.dip(10),
        )

        txt = f"{self._maximum:.0f} m"

        tw, th = gc.GetTextExtent(txt)

        gc.DrawText(
            txt,
            x + self.dip(12),
            bottom - th,
        )

        #
        # Position
        #

        ratio = (
            (self._length - self._minimum)
            /
            (self._maximum - self._minimum)
        )

        y = top + ratio * (bottom - top)

        #
        # Cable
        #

        gc.SetPen(
            wx.Pen(
                palette.primary,
                2,
            )
        )

        gc.StrokeLine(
            x,
            top,
            x,
            y,
        )

        #
        # Hook
        #

        r = self.dip(8)

        gc.SetBrush(
            wx.Brush(
                palette.primary
            )
        )

        gc.SetPen(wx.TRANSPARENT_PEN)

        gc.DrawEllipse(
            x - r,
            y - r,
            r * 2,
            r * 2,
        )