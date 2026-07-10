"""
Helicopter SAR Simulator
ui/controls/numeric_display.py
"""

from __future__ import annotations

import wx

from ui.base.base_widget import BaseWidget


class NumericDisplay(BaseWidget):

    PADDING = 12

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        title: str = "",
        value: float = 0.0,
        unit: str = "",
        decimals: int = 2,
        **kwargs,
    ):

        self._title = title
        self._value = value
        self._unit = unit
        self._decimals = decimals

        super().__init__(
            parent,
            id=id,
            **kwargs,
        )

        self.initialize()

    # ==================================================
    # Initialization
    # ==================================================

    def initialize(self):

        self.SetMinSize(
            (
                self.dip(180),
                self.dip(120),
            )
        )

    # ==================================================
    # Public API
    # ==================================================

    @property
    def value(self):

        return self._value

    def set_value(self, value: float):

        if value == self._value:
            return

        #print("NumericDisplay:", value)

        self._value = value
        self.Refresh()
        #self.Update()

    def set_title(self, title: str):

        self._title = title
        self.Refresh()

    def set_unit(self, unit: str):

        self._unit = unit
        self.Refresh()

    # ==================================================
    # Drawing
    # ==================================================

    #def draw_background(self, gc):
    #    w, h = self.GetClientSize()
    #
    #    gc.SetPen(wx.TRANSPARENT_PEN)
    #    gc.SetBrush(
    #        wx.Brush(self.palette.background)
    #    )
    #
    #    gc.DrawRectangle(
    #        0,
    #        0,
    #        w,
    #        h,
    #    )

    def draw(self, gc: wx.GraphicsContext):

        palette = self.palette

        width, height = self.GetClientSize()

        pad = self.dip(self.PADDING)

        #
        # Title
        #

        gc.SetFont(
            self.typography.body_small(),
            palette.text_secondary,
        )

        gc.DrawText(
            self._title,
            pad,
            pad,
        )

        #
        # Value
        #

        value_text = (
            f"{self._value:.{self._decimals}f}"
        )

        #
        # Font besar
        #

        #font = wx.Font(
        #    self.dip(28),
        #    wx.FONTFAMILY_SWISS,
        #    wx.FONTSTYLE_NORMAL,
        #    wx.FONTWEIGHT_BOLD,
        #)

        gc.SetFont(
            #font,
            self.typography.display_xl(),
            palette.text,
        )

        tw, th = gc.GetTextExtent(
            value_text
        )

        gc.DrawText(
            value_text,
            (width - tw) / 2,
            (height - th) / 2 - self.dip(8),
        )

        #
        # Unit
        #

        gc.SetFont(
            self.typography.body_small(),
            palette.text_secondary,
        )

        uw, uh = gc.GetTextExtent(
            self._unit
        )

        gc.DrawText(
            self._unit,
            (width - uw) / 2,
            (height - th) / 2 + th + self.dip(2),
        )