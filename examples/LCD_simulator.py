import wx


# ============================================================
# TFT CONFIGURATION
# ============================================================

TFT_WIDTH = 160
TFT_HEIGHT = 80

# Besar setiap pixel TFT pada simulator
SCALE = 6

WINDOW_WIDTH = TFT_WIDTH * SCALE
WINDOW_HEIGHT = TFT_HEIGHT * SCALE


# ============================================================
# TFT DISPLAY
# ============================================================

class TFTDisplay(wx.Panel):

    def __init__(self, parent):
        super().__init__(
            parent,
            size=(WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # ----------------------------------------------------
        # Virtual framebuffer 160x80
        # ----------------------------------------------------

        self.bitmap = wx.Bitmap(
            TFT_WIDTH,
            TFT_HEIGHT,
            depth=32
        )

        self.dc = wx.MemoryDC(self.bitmap)

        self.clear((10, 12, 16))

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    # --------------------------------------------------------
    # Basic TFT functions
    # --------------------------------------------------------

    def clear(self, color):
        self.dc.SetBackground(
            wx.Brush(wx.Colour(*color))
        )

        self.dc.Clear()

    def set_pixel(self, x, y, color):

        if not (0 <= x < TFT_WIDTH and 0 <= y < TFT_HEIGHT):
            return

        self.dc.SetPen(
            wx.Pen(wx.Colour(*color))
        )

        self.dc.DrawPoint(x, y)

    def draw_line(self, x1, y1, x2, y2, color):

        self.dc.SetPen(
            wx.Pen(wx.Colour(*color))
        )

        self.dc.DrawLine(x1, y1, x2, y2)

    def draw_rect(self, x, y, w, h, color, fill=False):

        if fill:
            self.dc.SetBrush(
                wx.Brush(wx.Colour(*color))
            )
        else:
            self.dc.SetBrush(wx.TRANSPARENT_BRUSH)

        self.dc.SetPen(
            wx.Pen(wx.Colour(*color))
        )

        self.dc.DrawRectangle(x, y, w, h)

    def draw_text(
        self,
        text,
        x,
        y,
        color=(255, 255, 255),
        size=10,
        bold=False
    ):

        font = wx.Font(
            size,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD if bold
            else wx.FONTWEIGHT_NORMAL
        )

        self.dc.SetFont(font)

        self.dc.SetTextForeground(
            wx.Colour(*color)
        )

        self.dc.DrawText(text, x, y)

    # --------------------------------------------------------
    # Refresh simulator
    # --------------------------------------------------------

    def refresh(self):

        self.Refresh(False)
        self.Update()

    # --------------------------------------------------------
    # Paint
    # --------------------------------------------------------

    def on_paint(self, event):

        paint_dc = wx.AutoBufferedPaintDC(self)

        paint_dc.SetBackground(
            wx.Brush(wx.Colour(30, 30, 30))
        )

        paint_dc.Clear()

        # Scale framebuffer 160x80 -> 960x480
        image = self.bitmap.ConvertToImage()

        image = image.Scale(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            wx.IMAGE_QUALITY_NEAREST
        )

        scaled_bitmap = wx.Bitmap(image)

        paint_dc.DrawBitmap(
            scaled_bitmap,
            0,
            0
        )

    def on_size(self, event):
        self.Refresh(False)
        event.Skip()


# ============================================================
# SOLDER STATION UI EXAMPLE
# ============================================================

class SolderStationUI:

    def __init__(self, display):

        self.display = display

        self.draw()

    def draw(self):

        tft = self.display

        # ----------------------------------------------------
        # Background
        # ----------------------------------------------------

        tft.clear((12, 15, 20))

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        tft.draw_rect(
            0, 0,
            160, 17,
            (25, 29, 36),
            fill=True
        )

        tft.draw_text(
            "T12 SOLDER",
            4, 3,
            (230, 230, 230),
            size=9,
            bold=True
        )

        # Status indicator
        tft.draw_rect(
            140, 5,
            8, 8,
            (40, 200, 90),
            fill=True
        )

        # ----------------------------------------------------
        # Temperature
        # ----------------------------------------------------

        tft.draw_text(
            "TEMP",
            7, 22,
            (150, 155, 165),
            size=8
        )

        tft.draw_text(
            "350",
            8, 32,
            (255, 170, 40),
            size=22,
            bold=True
        )

        tft.draw_text(
            "°C",
            65, 39,
            (220, 220, 220),
            size=10
        )

        # ----------------------------------------------------
        # Set temperature
        # ----------------------------------------------------

        tft.draw_text(
            "SET  350°C",
            93, 25,
            (180, 185, 195),
            size=8
        )

        # ----------------------------------------------------
        # Heater power bar
        # ----------------------------------------------------

        tft.draw_text(
            "POWER",
            93, 40,
            (150, 155, 165),
            size=7
        )

        tft.draw_rect(
            93, 51,
            58, 7,
            (50, 55, 65),
            fill=True
        )

        tft.draw_rect(
            93, 51,
            37, 7,
            (255, 140, 30),
            fill=True
        )

        # ----------------------------------------------------
        # Bottom status
        # ----------------------------------------------------

        tft.draw_line(
            0, 66,
            159, 66,
            (50, 55, 65)
        )

        tft.draw_text(
            "TIP",
            5, 69,
            (140, 145, 155),
            size=7
        )

        tft.draw_text(
            "T12-K",
            27, 69,
            (220, 220, 220),
            size=7,
            bold=True
        )

        tft.draw_text(
            "READY",
            113, 69,
            (50, 220, 100),
            size=7,
            bold=True
        )

        tft.refresh()


# ============================================================
# MAIN WINDOW
# ============================================================

class MainFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="TFT LCD Simulator — 160x80",
            size=(WINDOW_WIDTH + 16, WINDOW_HEIGHT + 39)
        )

        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.tft = TFTDisplay(panel)

        sizer.Add(
            self.tft,
            0,
            wx.ALL,
            0
        )

        panel.SetSizer(sizer)

        # Draw example UI
        self.ui = SolderStationUI(self.tft)

        self.Centre()


# ============================================================
# APPLICATION
# ============================================================

class App(wx.App):

    def OnInit(self):

        frame = MainFrame()
        frame.Show()

        return True


if __name__ == "__main__":

    app = App(False)
    app.MainLoop()