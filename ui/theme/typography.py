"""
Helicopter SAR Simulator
ui/theme/typography.py

Typography System

Seluruh font aplikasi harus berasal dari file ini.

Jangan pernah membuat wx.Font()
langsung di widget.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations
from dataclasses import dataclass

import wx


# ==========================================================
# Font Configuration
# ==========================================================

DEFAULT_FONT = "Segoe UI"
DEFAULT_WEIGHT = wx.FONTWEIGHT_NORMAL
DEFAULT_STYLE = wx.FONTSTYLE_NORMAL
DEFAULT_FAMILY = wx.FONTFAMILY_SWISS

# ==========================================================
# Font Style
# ==========================================================

@dataclass(frozen=True)
class FontStyle:
    """
    Menyimpan definisi sebuah style font.
    """

    point_size: int
    weight: int = DEFAULT_WEIGHT
    italic: bool = False
    underline: bool = False


# ==========================================================
# Typography Manager
# ==========================================================

class Typography:
    """
    Typography Manager.

    Seluruh font aplikasi diakses dari class ini.

    Example
    -------

    title.SetFont(Typography.heading())
    value.SetFont(Typography.display_large())
    label.SetFont(Typography.body())

    """

    _cache: dict[str, wx.Font] = {}

    # ------------------------------------------------------
    # Internal
    # ------------------------------------------------------

    @classmethod
    def _font(
        cls,
        key: str,
        style: FontStyle,
    ) -> wx.Font:

        if key in cls._cache:
            return cls._cache[key]

        font = wx.Font(
            pointSize=style.point_size,
            family=DEFAULT_FAMILY,
            style=wx.FONTSTYLE_ITALIC if style.italic else DEFAULT_STYLE,
            weight=style.weight,
            underline=style.underline,
            faceName=DEFAULT_FONT,
        )

        cls._cache[key] = font

        return font

    # ------------------------------------------------------
    # Display
    # ------------------------------------------------------

    @classmethod
    def display_xl(cls) -> wx.Font:
        return cls._font(
            "display_xl",
            FontStyle(
                28,
                wx.FONTWEIGHT_BOLD,
            ),
        )

    @classmethod
    def display_large(cls) -> wx.Font:
        return cls._font(
            "display_large",
            FontStyle(
                22,
                wx.FONTWEIGHT_BOLD,
            ),
        )

    @classmethod
    def display_medium(cls) -> wx.Font:
        return cls._font(
            "display_medium",
            FontStyle(
                18,
                wx.FONTWEIGHT_BOLD,
            ),
        )

    # ------------------------------------------------------
    # Heading
    # ------------------------------------------------------

    @classmethod
    def heading(cls) -> wx.Font:
        return cls._font(
            "heading",
            FontStyle(
                15,
                wx.FONTWEIGHT_BOLD,
            ),
        )

    @classmethod
    def subheading(cls) -> wx.Font:
        return cls._font(
            "subheading",
            FontStyle(
                13,
                wx.FONTWEIGHT_SEMIBOLD,
            ),
        )

    # ------------------------------------------------------
    # Body
    # ------------------------------------------------------

    @classmethod
    def body(cls) -> wx.Font:
        return cls._font(
            "body",
            FontStyle(
                11,
            ),
        )
    
    @classmethod
    def body_small(cls) -> wx.Font:
        return cls._font(
            "body_small",
            FontStyle(
                9,
                wx.FONTWEIGHT_NORMAL,
            )
        )

    @classmethod
    def body_bold(cls) -> wx.Font:
        return cls._font(
            "body_bold",
            FontStyle(
                11,
                wx.FONTWEIGHT_BOLD,
            ),
        )

    @classmethod
    def caption(cls) -> wx.Font:
        return cls._font(
            "caption",
            FontStyle(
                9,
            ),
        )

    @classmethod
    def small(cls) -> wx.Font:
        return cls._font(
            "small",
            FontStyle(
                8,
            ),
        )

    # ------------------------------------------------------
    # Utility
    # ------------------------------------------------------

    @classmethod
    def clear_cache(cls) -> None:
        """
        Menghapus cache font.

        Digunakan jika suatu saat
        font aplikasi diganti.
        """

        cls._cache.clear()