from __future__ import annotations

import math
import wx

from ui.base.base_panel import BasePanel


class SeaView(BasePanel):

    def __init__(self, parent, **kwargs):

        self._phase = 0.0

        super().__init__(parent, **kwargs)

    # --------------------------------------------------

    def set_phase(self, phase: float):

        self._phase = phase
        self.Refresh(False)

    # --------------------------------------------------

    def draw_foreground(self, gc):

        w, h = self.GetClientSize()

        sea_top = int(h * 0.65)

        #
        # Sea
        #

        gc.SetBrush(
            wx.Brush(self.palette.info)
        )

        gc.SetPen(wx.TRANSPARENT_PEN)

        path = gc.CreatePath()

        path.MoveToPoint(0, sea_top)

        for x in range(w + 1):

            y = (
                sea_top
                + math.sin(
                    (x * 0.03) + self._phase
                ) * 6
            )

            path.AddLineToPoint(x, y)

        path.AddLineToPoint(w, h)
        path.AddLineToPoint(0, h)
        path.CloseSubpath()

        gc.DrawPath(path)