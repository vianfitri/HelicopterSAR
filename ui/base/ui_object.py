"""
Helicopter SAR Simulator
ui/base/ui_object.py

Shared helper untuk seluruh komponen UI.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

from typing import Tuple

import wx

from ui.theme.metrics import Metrics
from ui.theme.palette import ThemeManager
from ui.theme.typography import Typography


class UIObjectMixin:
    """
    Shared helper untuk BaseWidget dan BasePanel.
    """

    # ======================================================
    # Theme
    # ======================================================

    @property
    def palette(self):
        return ThemeManager.current()

    # ======================================================
    # Metrics
    # ======================================================

    @property
    def metrics(self):
        return Metrics
    
    # ======================================================
    # Typography
    # ======================================================

    @property
    def typography(self):
        return Typography

    # ======================================================
    # Geometry
    # ======================================================

    @property
    def width(self) -> int:
        return self.GetClientSize().width

    @property
    def height(self) -> int:
        return self.GetClientSize().height

    @property
    def size(self) -> wx.Size:
        return self.GetClientSize()

    @property
    def rect(self) -> wx.Rect:
        return self.GetClientRect()

    @property
    def center(self) -> Tuple[int, int]:
        r = self.rect
        return (r.width // 2, r.height // 2)

    # ======================================================
    # DPI
    # ======================================================

    def dip(self, value: int) -> int:
        return self.FromDIP(value)

    # ======================================================
    # Refresh
    # ======================================================

    def invalidate(self) -> None:
        self.Refresh(False)

    def update_now(self) -> None:
        self.Update()

    # ======================================================
    # Batch Update
    # ======================================================

    def begin_update(self) -> None:
        self.Freeze()

    def end_update(self) -> None:
        self.Thaw()
        self.invalidate()

    # ======================================================
    # State
    # ======================================================

    def show(self) -> None:
        self.Show()

    def hide(self) -> None:
        self.Hide()

    def enable(self) -> None:
        self.Enable()

    def disable(self) -> None:
        self.Disable()

    def focus(self) -> None:
        self.SetFocus()

    # ======================================================
    # Cursor
    # ======================================================

    def set_hand_cursor(self) -> None:
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def set_arrow_cursor(self) -> None:
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def set_cross_cursor(self) -> None:
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))