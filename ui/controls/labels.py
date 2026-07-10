"""
Helicopter SAR Simulator
ui/controls/label.py

Modern Label Control.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

import wx

from ui.theme.typography import Typography
from ui.base.ui_object import UIObjectMixin
from ui.theme.palette import ThemeManager


class Label(UIObjectMixin, wx.StaticText):
    """
    Modern label untuk seluruh aplikasi.

    Jangan menggunakan wx.StaticText secara langsung.
    """

    def __init__(
        self,
        parent: wx.Window,
        text: str = "",
        *,
        font: wx.Font,
        colour: wx.Colour,
        style: int = 0,
    ) -> None:

        super().__init__(
            parent,
            label=text,
            style=style,
        )

        self.SetFont(font)
        self.SetForegroundColour(colour)

    # =====================================================
    # Factory
    # =====================================================

    @classmethod
    def title(
        cls,
        parent: wx.Window,
        text: str,
    ) -> "Label":

        return cls(
            parent,
            text,
            font=Typography.heading(),
            colour=cls._palette().text,
        )

    @classmethod
    def subtitle(
        cls,
        parent: wx.Window,
        text: str,
    ) -> "Label":

        return cls(
            parent,
            text,
            font=Typography.subheading(),
            colour=cls._palette().text_secondary,
        )

    @classmethod
    def body(
        cls,
        parent: wx.Window,
        text: str,
    ) -> "Label":

        return cls(
            parent,
            text,
            font=Typography.body(),
            colour=cls._palette().text,
        )

    @classmethod
    def caption(
        cls,
        parent: wx.Window,
        text: str,
    ) -> "Label":

        return cls(
            parent,
            text,
            font=Typography.caption(),
            colour=cls._palette().text_secondary,
        )

    @classmethod
    def display(
        cls,
        parent: wx.Window,
        text: str,
    ) -> "Label":

        return cls(
            parent,
            text,
            font=Typography.display_large(),
            colour=cls._palette().primary,
        )

    @classmethod
    def status(
        cls,
        parent: wx.Window,
        text: str,
        colour: wx.Colour | None = None,
    ) -> "Label":

        return cls(
            parent,
            text,
            font=Typography.body_bold(),
            colour=colour or cls._palette().success,
        )

    # =====================================================
    # Helper
    # =====================================================

    @staticmethod
    def _palette():
        return ThemeManager.current()

    def set_text(self, text: str) -> None:
        """
        Mengubah isi label.
        """
        self.SetLabel(text)

    def set_colour(self, colour: wx.Colour) -> None:
        """
        Mengubah warna teks.
        """
        self.SetForegroundColour(colour)

    def set_font(self, font: wx.Font) -> None:
        """
        Mengubah font.
        """
        self.SetFont(font)