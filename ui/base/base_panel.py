"""
Helicopter SAR Simulator
ui/base/base_panel.py

Base class untuk seluruh panel AeroSAR.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

import wx

from ui.base.ui_object import UIObjectMixin


class BasePanel(UIObjectMixin, wx.Panel):
    """
    Base class seluruh panel.

    Semua panel besar sebaiknya
    mewarisi class ini.

    Contoh:
        Header
        Sidebar
        Toolbar
        Card
        Telemetry
        Helicopter Track
        Hoist Panel
        
    Lifecycle:
        __init__()
            └── initialize()

    Subclass hanya perlu mengimplementasikan initialize()
    dan tidak perlu memanggilnya sendiri.  
    """

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.BORDER_NONE,
        name: str = "BasePanel",
    ) -> None:

        super().__init__(
            parent,
            id=id,
            pos=pos,
            size=size,
            style=style,
            name=name,
        )

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour(self.palette.background)

        self.SetMinSize((
            self.dip(self.metrics.widget.min_size),
            self.dip(self.metrics.widget.min_size),
        ))

        if hasattr(self, "SetDoubleBuffered"):
            self.SetDoubleBuffered(True)
        
        self._content_sizer: wx.Sizer | None = None

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)

        self.initialize()

    # ======================================================
    # Initialization Hook
    # ======================================================

    def initialize(self) -> None:
        """
        Hook untuk subclass
        Override bila diperlukan
        """ 

        return

    # ======================================================
    # Layout
    # ======================================================

    @property
    def content_sizer(self) -> wx.Sizer | None:
        return self._content_sizer
    
    def set_content_sizer(self, sizer: wx.Sizer) -> None:
        """
        mengatur size utama panel
        """

        self._content_sizer = sizer
        self.SetSizer(sizer)
        self.Layout()

    # ======================================================
    # Internal
    # ======================================================

    def _create_graphics_context(self, dc: wx.DC) -> wx.GraphicsContext:
        gc = wx.GraphicsContext.Create(dc)

        if gc is None:
            raise RuntimeError("Failed to create GraphicsContext.")
        
        return gc

    # ======================================================
    # Events
    # ======================================================

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.Layout()
        self.invalidate()
        event.Skip()

    def _on_paint(self, event: wx.PaintEvent) -> None:

        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        gc = self._create_graphics_context(dc)

        self.draw_background(gc)
        self.draw_foreground(gc)
        self.draw_debug(gc)
        event.Skip(False)

    # ======================================================
    # Paint Pipeline
    # ======================================================

    def draw_background(self, gc: wx.GraphicsContext) -> None:

        """
        Background panel.

        Override bila perlu.
        """

        return

    def draw_foreground(self, gc: wx.GraphicsContext) -> None:

        """
        Overlay.

        Misalnya:
        watermark
        selection
        crosshair
        dsb.
        """

        return

    def draw_debug(self, gc: wx.GraphicsContext) -> None:

        """
        Debug Layer.

        Grid
        FPS
        Layout
        Bounds
        """

        return