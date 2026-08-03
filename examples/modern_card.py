"""
modern_card.py
Reusable Modern Card
Compatible : wxPython 4.2.5

Author : ChatGPT
"""

import math
import wx


# ============================================================
# Default Theme
# ============================================================

class CardTheme:

    BACKGROUND = wx.Colour(255, 255, 255)

    BORDER = wx.Colour(210, 214, 220)

    HEADER = wx.Colour(250, 250, 250)

    TEXT = wx.Colour(40, 40, 40)

    SUBTEXT = wx.Colour(110, 110, 110)

    ACCENT = wx.Colour(255, 130, 0)

    SHADOW = wx.Colour(0, 0, 0, 20)


# ============================================================
# Utility
# ============================================================

def lighten(colour, amount):

    r = min(255, colour.Red() + amount)
    g = min(255, colour.Green() + amount)
    b = min(255, colour.Blue() + amount)

    return wx.Colour(r, g, b)


def darken(colour, amount):

    r = max(0, colour.Red() - amount)
    g = max(0, colour.Green() - amount)
    b = max(0, colour.Blue() - amount)

    return wx.Colour(r, g, b)


# ============================================================
# Shadow Painter
# ============================================================

class ShadowPainter:
    """
    Fake gaussian shadow.
    Dibuat dari beberapa rounded rectangle
    dengan alpha yang semakin kecil.

    Tidak membutuhkan bitmap maupun image blur.
    """

    @staticmethod
    def draw(gc,
             x,
             y,
             w,
             h,
             radius,
             shadow_size=8):

        if shadow_size <= 0:
            return

        for i in range(shadow_size):

            alpha = int(
                28 *
                (1.0 - (i / float(shadow_size)))
            )

            c = wx.Colour(0, 0, 0, alpha)

            path = gc.CreatePath()

            expand = shadow_size - i

            path.AddRoundedRectangle(
                x - expand,
                y - expand,
                w + expand * 2,
                h + expand * 2,
                radius + expand
            )

            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.SetBrush(wx.Brush(c))

            gc.FillPath(path)


# ============================================================
# Content Panel
# ============================================================

class CardContent(wx.Panel):
    """
    Panel tempat user meletakkan widget.

    Tidak menggambar background.
    Background digambar oleh ModernCard.
    """

    def __init__(self, parent):

        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onErase)

        self.Bind(wx.EVT_PAINT, self.onPaint)

    def onErase(self, event):
        pass

    def onPaint(self, event):

        dc = wx.AutoBufferedPaintDC(self)

        dc.SetBackground(
            wx.Brush(
                self.GetParent().background_colour
            )
        )

        dc.Clear()


# ============================================================
# Modern Card
# ============================================================

class ModernCard(wx.Panel):

    HEADER_LEFT = 0
    HEADER_CENTER = 1
    HEADER_RIGHT = 2

    def __init__(
            self,
            parent,

            title="Card",

            icon=None,

            size=(-1, -1),

            radius=14,

            padding=12,

            header_height=42,

            shadow_size=8,

            show_header=True,

            background_colour=CardTheme.BACKGROUND,

            border_colour=CardTheme.BORDER,

            header_colour=CardTheme.HEADER,

            text_colour=CardTheme.TEXT,

            accent_colour=CardTheme.ACCENT,

            font=None,
    ):

        super().__init__(
            parent,
            size=size,
            style=wx.BORDER_NONE
        )

        # ------------------------------------------

        self.SetBackgroundStyle(
            wx.BG_STYLE_PAINT
        )

        self.SetDoubleBuffered(True)

        # ------------------------------------------

        if font is None:

            self.font = wx.Font(
                10,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
                False,
                "Segoe UI"
            )

        else:

            self.font = font

        # ------------------------------------------

        self.title = title

        self.icon = icon

        self.radius = radius

        self.padding = padding

        self.header_height = header_height

        self.shadow_size = shadow_size

        self.show_header = show_header

        self.header_alignment = ModernCard.HEADER_LEFT

        # ------------------------------------------

        self.background_colour = background_colour

        self.border_colour = border_colour

        self.header_colour = header_colour

        self.text_colour = text_colour

        self.accent_colour = accent_colour

        self.border_width = 1

        self.show_border = True

        self.show_shadow = True

        self.show_accent = False

        self.hover = False

        self.hover_colour = lighten(
            background_colour,
            6
        )

        # dibuat di bagian berikutnya:
        # self.content
        # layout
        # event binding

            # -------------------------------------------------------
        # Content Panel
        # -------------------------------------------------------

        self.content = CardContent(self)

        # Content panel menggunakan warna yang sama dengan card
        self.content.SetBackgroundColour(
            self.background_colour
        )

        # -------------------------------------------------------
        # Layout
        # -------------------------------------------------------

        self._build_layout()

        # -------------------------------------------------------
        # Event
        # -------------------------------------------------------

        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_SIZE, self.onSize)

        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)

    # ============================================================
    # Layout
    # ============================================================

    def _build_layout(self):

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        top = self.padding

        if self.show_header:
            top += self.header_height

        self.mainSizer.AddSpacer(top)

        self.mainSizer.Add(
            self.content,
            1,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            self.padding
        )

        self.SetSizer(self.mainSizer)

    # ============================================================
    # Public API
    # ============================================================

    @property
    def Content(self):
        """
        Panel yang dapat diisi widget.
        """

        return self.content

    # ------------------------------------------------------------

    def GetContentPanel(self):
        return self.content

    # ------------------------------------------------------------

    def SetContentSizer(self, sizer):

        self.content.SetSizer(sizer)

    # ------------------------------------------------------------

    def SetPadding(self, padding):

        self.padding = padding

        self.mainSizer.Clear(False)

        self._build_layout()

        self.Layout()

        self.Refresh()

    # ------------------------------------------------------------

    def SetRadius(self, radius):

        self.radius = radius

        self.Refresh()

    # ------------------------------------------------------------

    def SetShadowSize(self, size):

        self.shadow_size = max(0, size)

        self.Refresh()

    # ------------------------------------------------------------

    def EnableShadow(self, enable=True):

        self.show_shadow = enable

        self.Refresh()

    # ------------------------------------------------------------

    def EnableBorder(self, enable=True):

        self.show_border = enable

        self.Refresh()

    # ------------------------------------------------------------

    def EnableAccent(self, enable=True):

        self.show_accent = enable

        self.Refresh()

    # ------------------------------------------------------------

    def SetBorderWidth(self, width):

        self.border_width = width

        self.Refresh()

    # ------------------------------------------------------------

    def SetBackgroundColour(self, colour):

        self.background_colour = colour

        if hasattr(self, "content"):
            self.content.SetBackgroundColour(colour)

        self.Refresh()

    # ------------------------------------------------------------

    def SetBorderColour(self, colour):

        self.border_colour = colour

        self.Refresh()

    # ------------------------------------------------------------

    def SetAccentColour(self, colour):

        self.accent_colour = colour

        self.Refresh()

    # ------------------------------------------------------------

    def SetHeaderColour(self, colour):

        self.header_colour = colour

        self.Refresh()

    # ------------------------------------------------------------

    def SetTitleColour(self, colour):

        self.text_colour = colour

        self.Refresh()

    # ------------------------------------------------------------

    def SetHeaderHeight(self, height):

        self.header_height = height

        self.mainSizer.Clear(False)

        self._build_layout()

        self.Layout()

        self.Refresh()

    # ------------------------------------------------------------

    def ShowHeader(self, show=True):

        self.show_header = show

        self.mainSizer.Clear(False)

        self._build_layout()

        self.Layout()

        self.Refresh()

    # ------------------------------------------------------------

    def SetTitle(self, title):

        self.title = title

        self.Refresh()

    # ------------------------------------------------------------

    def SetTitleFont(self, font):

        self.font = font

        self.Refresh()

    # ------------------------------------------------------------

    def SetTitleAlignment(self, alignment):

        self.header_alignment = alignment

        self.Refresh()

    # ------------------------------------------------------------

    def SetIcon(self, bitmap):

        self.icon = bitmap

        self.Refresh()

    # ============================================================
    # Mouse
    # ============================================================

    def onMouseEnter(self, event):

        self.hover = True

        self.Refresh()

        event.Skip()

    # ------------------------------------------------------------

    def onMouseLeave(self, event):

        self.hover = False

        self.Refresh()

        event.Skip()

    # ============================================================
    # Window Event
    # ============================================================

    def onEraseBackground(self, event):
        """
        Menghindari flicker.
        """
        pass

    # ------------------------------------------------------------

    def onSize(self, event):

        self.Refresh()

        event.Skip()

    # ============================================================
    # Drawing Helper
    # ============================================================

    def _createRoundedPath(
            self,
            gc,
            x,
            y,
            w,
            h,
            radius):

        path = gc.CreatePath()

        path.AddRoundedRectangle(
            x,
            y,
            w,
            h,
            radius
        )

        return path

    # ------------------------------------------------------------

    def _drawRoundedRect(
            self,
            gc,
            x,
            y,
            w,
            h,
            radius,
            colour):

        path = self._createRoundedPath(
            gc,
            x,
            y,
            w,
            h,
            radius
        )

        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.SetBrush(wx.Brush(colour))

        gc.FillPath(path)

    # ------------------------------------------------------------

    def _drawBorder(
            self,
            gc,
            x,
            y,
            w,
            h):

        if not self.show_border:
            return

        path = self._createRoundedPath(
            gc,
            x,
            y,
            w,
            h,
            self.radius
        )

        gc.SetBrush(wx.TRANSPARENT_BRUSH)

        gc.SetPen(
            wx.Pen(
                self.border_colour,
                self.border_width
            )
        )

        gc.DrawPath(path)

    # ============================================================
    # Paint
    # ============================================================

    def onPaint(self, event):
        """
        Diimplementasikan penuh pada Bagian 3.
        """
        pass

    