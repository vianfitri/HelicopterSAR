"""
Helicopter SAR Simulator
ui/theme/palette.py

Theme color definitions.

Author : Mas Vi & ChatGPT
Version: 0.1.0
"""

from __future__ import annotations
from dataclasses import dataclass

import wx

# ==========================================================
# Helper
# ==========================================================

def rgb(value: str) -> wx.Colour:
    """
    Change HEX string to wx.Colour.

    Example
    -------
    rgb("#3BA7FF")
    """

    value = value.lstrip("#")

    return wx.Colour(
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )

# ==========================================================
# Theme Dataclass
# ==========================================================

@dataclass(frozen=True)
class ThemePalette:
    """
    All application color.
    """

    # ------------------------------------------------------
    # Background
    # ------------------------------------------------------

    background: wx.Colour
    panel: wx.Colour
    panel_alt: wx.Colour
    card: wx.Colour
    border: wx.Colour
    separator: wx.Colour
    shadow: wx.Colour

    # ------------------------------------------------------
    # Primary
    # ------------------------------------------------------

    primary: wx.Colour
    primary_hover: wx.Colour
    primary_pressed: wx.Colour

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    success: wx.Colour
    warning: wx.Colour
    danger: wx.Colour
    info: wx.Colour

    # ------------------------------------------------------
    # Text
    # ------------------------------------------------------

    text: wx.Colour
    text_secondary: wx.Colour
    text_disabled: wx.Colour

    # ------------------------------------------------------
    # Indicator
    # ------------------------------------------------------

    led_on: wx.Colour
    led_warning: wx.Colour
    led_error: wx.Colour
    led_off: wx.Colour

    # ------------------------------------------------------
    # Graph
    # ------------------------------------------------------

    graph_grid: wx.Colour
    graph_axis: wx.Colour
    graph_line: wx.Colour
    graph_fill: wx.Colour

 # ==========================================================
# Dark Theme
# ==========================================================

DARK = ThemePalette(
    background=rgb("#0F1722"),
    panel=rgb("#182232"),
    panel_alt=rgb("#202D40"),
    card=rgb("#223147"),
    border=rgb("#304258"),
    separator=rgb("#2A3749"),
    shadow=rgb("#081018"),
    primary=rgb("#3BA7FF"),
    primary_hover=rgb("#56B6FF"),
    primary_pressed=rgb("#1D8AE6"),
    success=rgb("#31D07B"),
    warning=rgb("#F7A928"),
    danger=rgb("#F04646"),
    info=rgb("#47C2FF"),
    text=rgb("#F4F7FA"),
    text_secondary=rgb("#B4BFCC"),
    text_disabled=rgb("#738196"),
    led_on=rgb("#35D87F"),
    led_warning=rgb("#FFB020"),
    led_error=rgb("#FF4A4A"),
    led_off=rgb("#4C596B"),
    graph_grid=rgb("#2D3C50"),
    graph_axis=rgb("#64748B"),
    graph_line=rgb("#39A8FF"),
    graph_fill=rgb("#16395C"),
)


# ==========================================================
# Theme Manager
# ==========================================================

class ThemeManager:
    """
    Singleton sederhana untuk mengelola theme aktif.
    """

    _theme: ThemePalette = DARK

    @classmethod
    def current(cls) -> ThemePalette:
        return cls._theme

    @classmethod
    def set_theme(cls, theme: ThemePalette) -> None:
        cls._theme = theme


# Shortcut
Theme = ThemeManager.current()   
