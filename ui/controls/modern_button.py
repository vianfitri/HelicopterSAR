"""
Helicopter SAR Simulator
ui/controls/modern_button.py

Modern flat button.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

import wx

from ui.base.base_widget import BaseWidget


# ==========================================================
# Constants
# ==========================================================

BUTTON_HEIGHT = 40
BUTTON_MIN_WIDTH = 120
BUTTON_RADIUS = 8


# ==========================================================
# ModernButton
# ==========================================================

class ModernButton(BaseWidget):

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        label: str = "",
        **kwargs,
    ) -> None:

        self._label = label

        self._hover = False
        self._pressed = False

        super().__init__(
            parent,
            id=id,
            **kwargs,
        )

        self.initialize()
        self.bind_events()

    # ======================================================
    # Initialize
    # ======================================================

    def initialize(self):

        self.SetMinSize((
            self.dip(BUTTON_MIN_WIDTH),
            self.dip(BUTTON_HEIGHT),
        ))

        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    # ======================================================
    # Events
    # ======================================================

    def bind_events(self):

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    # ------------------------------------------------------

    def on_enter(self, event):

        if self.IsEnabled():

            self._hover = True
            self.Refresh()

        event.Skip()

    # ------------------------------------------------------

    def on_leave(self, event):

        self._hover = False
        #self._pressed = False

        self.Refresh()

        event.Skip()

    # ------------------------------------------------------

    def on_left_down(self, event):

        if not self.IsEnabled():
            return

        self._pressed = True

        if not self.HasCapture():
            self.CaptureMouse()

        self.Refresh()
        self.Update()

        event.Skip()

    # ------------------------------------------------------

    def on_left_up(self, event):

        if not self.IsEnabled():
            return

        if self.HasCapture():
            self.ReleaseMouse()

        inside = self.GetClientRect().Contains(
            event.GetPosition()
        )

        clicked = self._pressed and inside
        self._pressed = False
        self.Refresh()

        if clicked:

            evt = wx.CommandEvent(
                wx.EVT_BUTTON.typeId,
                self.GetId(),
            )

            evt.SetEventObject(self)

            self.ProcessWindowEvent(evt)

        event.Skip()

    # ======================================================
    # Paint
    # ======================================================

    def draw(self, gc: wx.GraphicsContext):
        palette = self.palette
        width, height = self.GetClientSize()
        radius = self.dip(BUTTON_RADIUS)

        if not self.IsEnabled():
            fill = palette.panel_alt
            text = palette.text_disabled

        elif self._pressed:
            fill = palette.primary_pressed
            text = palette.text

        elif self._hover:
            fill = palette.primary_hover
            text = palette.text

        else:
            fill = palette.primary
            text = palette.text
        
        gc.SetBrush(wx.Brush(fill))

        gc.SetPen(wx.Pen(palette.border, 1))

        gc.DrawRoundedRectangle(0, 0, width, height, radius)

        gc.SetFont(self.typography.body_bold(), text)

        tw, th = gc.GetTextExtent(self._label)

        x = (width - tw) /2
        y = (height - th) /2

        gc.DrawText(self._label, x, y)



    """
    def draw_background(self, gc):

        rect = self.GetClientRect()
        radius = self.dip(BUTTON_RADIUS)
        palette = self.palette

        if not self.IsEnabled():
            fill = palette.panel_alt
            text = palette.text_disabled

        elif self._pressed:
            fill = palette.primary_pressed
            text = palette.text

        elif self._hover:
            fill = palette.primary_hover
            text = palette.text

        else:
            fill = palette.primary
            text = palette.text

        self._text_colour = text

        gc.SetBrush(
            wx.Brush(fill)
        )

        gc.SetPen(
            wx.Pen(
                palette.border,
                1,
            )
        )

        gc.DrawRoundedRectangle(
            0,
            0,
            rect.width,
            rect.height,
            radius,
        )
    """

    # ------------------------------------------------------

    """
    def draw_foreground(self, gc):

        rect = self.GetClientRect()

        gc.SetFont(
            self.typography.body_bold(),
            self._text_colour,
        )

        tw, th = gc.GetTextExtent(
            self._label
        )

        x = (rect.width - tw) / 2
        y = (rect.height - th) / 2

        gc.DrawText(
            self._label,
            x,
            y,
        )
    """

    # ======================================================
    # Public API
    # ======================================================

    @property
    def label(self):

        return self._label

    # ------------------------------------------------------

    def set_label(
        self,
        text: str,
    ):

        self._label = text
        self.Refresh()