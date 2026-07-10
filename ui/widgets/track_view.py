from __future__ import annotations

import wx

from ui.base.base_widget import BaseWidget


class TrackView(BaseWidget):

    TRACK_MARGIN = 40

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
        self._position = value

        super().__init__(
            parent,
            id=id,
            **kwargs,
        )

        self.initialize()

    # ======================================================
    # Initialization
    # ======================================================

    def initialize(self):

        self.SetMinSize(
            (
                self.dip(500),
                self.dip(140),
            )
        )

    # ======================================================
    # Property
    # ======================================================

    @property
    def position(self) -> float:
        return self._position

    @property
    def minimum(self) -> float:
        return self._minimum

    @property
    def maximum(self) -> float:
        return self._maximum

    # ======================================================
    # Public
    # ======================================================

    def set_position(self, value: float):

        value = max(
            self._minimum,
            min(self._maximum, value)
        )

        if value == self._position:
            return

        self._position = value

        self.Refresh()

    # ======================================================
    # Draw
    # ======================================================

    def draw(self, gc: wx.GraphicsContext):

        palette = self.palette

        w, h = self.GetClientSize()

        margin = self.dip(self.TRACK_MARGIN)

        y = h // 2

        #
        # Track
        #

        gc.SetPen(
            wx.Pen(
                palette.graph_axis,
                2,
            )
        )

        gc.StrokeLine(
            margin,
            y,
            w - margin,
            y,
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
            margin - self.dip(12),
            y + self.dip(12),
        )

        tw, th = gc.GetTextExtent(
            f"{self._maximum:.0f} m"
        )

        gc.DrawText(
            f"{self._maximum:.0f} m",
            w - margin - tw + self.dip(12),
            y + self.dip(12),
        )

        #
        # Marker Position
        #

        ratio = (
            (self._position - self._minimum)
            /
            (self._maximum - self._minimum)
        )

        x = margin + ratio * (w - margin * 2)

        #
        # Vertical Line
        #

        gc.SetPen(
            wx.Pen(
                palette.primary,
                2,
            )
        )

        gc.StrokeLine(
            x,
            y - self.dip(28),
            x,
            y,
        )

        #
        # Triangle
        #

        path = gc.CreatePath()

        size = self.dip(8)

        path.MoveToPoint(x, y - self.dip(40))
        path.AddLineToPoint(x - size, y - self.dip(28))
        path.AddLineToPoint(x + size, y - self.dip(28))
        path.CloseSubpath()

        gc.SetBrush(
            wx.Brush(
                palette.primary
            )
        )

        gc.SetPen(wx.TRANSPARENT_PEN)

        gc.DrawPath(path)