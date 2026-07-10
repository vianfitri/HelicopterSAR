"""
Helicopter SAR Simulator
ui/base/base_widget.py

Base class untuk seluruh custom widget.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations
from typing import Tuple
import wx
from ui.base.ui_object import UIObjectMixin


class BaseWidget(UIObjectMixin, wx.Control):
    """
    Base class seluruh custom widget Helicopter SAR.

    Semua widget kecil seperti:

        - Button
        - Slider
        - LED
        - NumericDisplay
        - Label

    sebaiknya mewarisi class ini.
    """

    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.BORDER_NONE,
        name: str = "BaseWidget",
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
        self.SetBackgroundColour(self.palette.background
        )

        size = self.dip(self.metrics.widget.min_size)

        self.SetMinSize((size,size))

        if hasattr(self, "SetDoubleBuffered"):
            self.SetDoubleBuffered(True)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)


    # --------------------------------------------------
    # Initialization Hook
    # --------------------------------------------------

    def initialize(self) -> None:
        """
        Hook untuk subclass

        Override jika widget membutuhkan
        inisialisasi tambahan
        """

        return

    # --------------------------------------------------
    # Internal
    # --------------------------------------------------

    def _create_graphics_context(self, dc: wx.DC) -> wx.GraphicsContext:
        gc = wx.GraphicsContext.Create(dc)

        if gc is None:
            raise RuntimeError("Failed to create GraphicsContext.")
        
        return gc

    # --------------------------------------------------
    # Events
    # --------------------------------------------------

    def _on_paint(self, event: wx.PaintEvent) -> None:
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        gc = self._create_graphics_context(dc)
        
        self.draw_background(gc)
        self.draw(gc)
        self.draw_foreground(gc)
        self.draw_debug(gc)

        event.Skip(False)

    def _on_size(self, event: wx.SizeEvent) -> None:
        self.invalidate()
        event.Skip()

    # --------------------------------------------------
    # Paint Pipeline
    # --------------------------------------------------

    def draw_background(self, gc: wx.GraphicsContext) -> None:
        
        """
        Background layer.
        Override bila diperlukan
        """

        return

    def draw(self, gc: wx.GraphicsContext) -> None:
        """
        Override pada subclass.

        Main drawing.
        """

        raise NotImplementedError(
            f"{self.__class__.__name__}.draw() belum diimplementasikan."
        )
    
    def draw_foreground(self, gc: wx.GraphicsContext) -> None:
        """
        Overlay layer.
        """

        return

    def draw_debug(self, gc: wx.GraphicsContext) -> None:
        """
        Layer debug
        Use if ENABLE_DEBUG = True
        """

        return