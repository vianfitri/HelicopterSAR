"""
Helicopter SAR Simulator
ui/panels/modern_card.py

Modern dashboard card.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

import wx

from ui.base.base_panel import BasePanel
from ui.controls.labels import Label


class ModernCard(BasePanel):
    """
    Modern dashboard card.

    +--------------------------------------+
    | Header                               |
    +--------------------------------------+
    |                                      |
    | Body                                 |
    |                                      |
    +--------------------------------------+
    | Footer                               |
    +--------------------------------------+
    """

    def __init__(
        self,
        parent: wx.Window,
        title: str = "",
        **kwargs,
    ) -> None:

        self._title = title

        super().__init__(parent, **kwargs)

        #self.initialize()

    # =====================================================
    # Initialization
    # =====================================================

    def initialize(self) -> None:

        self._create_widgets()
        self._create_layout()
        self._apply_theme()

    # =====================================================
    # Create
    # =====================================================

    def _create_widgets(self) -> None:

        self._header_panel = BasePanel(self)
        self._body_panel = BasePanel(self)
        self._footer_panel = BasePanel(self)

        self._title_label = Label.title(
            self._header_panel,
            self._title,
        )

        self._header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._body_sizer = wx.BoxSizer(wx.VERTICAL)
        self._footer_sizer = wx.BoxSizer(wx.HORIZONTAL)

    def _create_layout(self) -> None:

        spacing = self.dip(self.metrics.spacing.medium)

        self._header_sizer.Add(
            self._title_label,
            0,
            wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            spacing,
        )

        self._header_panel.set_content_sizer(
            self._header_sizer
        )

        self._body_panel.set_content_sizer(
            self._body_sizer
        )

        self._footer_panel.set_content_sizer(
            self._footer_sizer
        )

        main = wx.BoxSizer(wx.VERTICAL)

        main.Add(
            self._header_panel,
            0,
            wx.EXPAND,
        )

        main.Add(
            self._body_panel,
            1,
            wx.EXPAND,
        )

        main.Add(
            self._footer_panel,
            0,
            wx.EXPAND,
        )

        self.set_content_sizer(main)

    # =====================================================
    # Theme
    # =====================================================

    def _apply_theme(self) -> None:

        p = self.palette

        self.SetBackgroundColour(p.card)

        self._header_panel.SetBackgroundColour(
            #p.surface
            p.card
        )

        self._body_panel.SetBackgroundColour(
            p.card
        )

        self._footer_panel.SetBackgroundColour(
            #p.surface
            p.card
        )

    # =====================================================
    # Public API
    # =====================================================

    @property
    def body_panel(self) -> BasePanel:
        return self._body_panel

    @property
    def body_sizer(self) -> wx.BoxSizer:
        return self._body_sizer

    @property
    def footer_panel(self) -> BasePanel:
        return self._footer_panel

    @property
    def footer_sizer(self) -> wx.BoxSizer:
        return self._footer_sizer

    @property
    def title(self) -> str:
        return self._title

    def set_title(
        self,
        text: str,
    ) -> None:

        self._title = text
        self._title_label.set_text(text)