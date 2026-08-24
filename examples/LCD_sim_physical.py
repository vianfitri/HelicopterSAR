import wx


# ============================================================
# TFT SPECIFICATION
# ============================================================

TFT_WIDTH = 160
TFT_HEIGHT = 80

# Ukuran fisik panel TFT
TFT_PHYSICAL_WIDTH_MM = 21.7
TFT_PHYSICAL_HEIGHT_MM = 10.8

# ============================================================
# MONITOR
# ============================================================

# Masukkan PPI monitor kamu di sini.
#
# Contoh:
#   96
#   110
#   120
#   144
#   163
#
# Ini BUKAN PPI TFT.
#
MONITOR_PPI = 96


# ============================================================
# DISPLAY MODE
# ============================================================

MODE_PHYSICAL = "physical"
MODE_1X = "1x"
MODE_ZOOM = "zoom"


DISPLAY_MODE = MODE_ZOOM

# Hanya digunakan jika MODE_ZOOM
ZOOM = 6


# ============================================================
# CALCULATE DISPLAY SIZE
# ============================================================

def mm_to_pixel(mm, ppi):
    """
    Mengubah ukuran mm menjadi pixel monitor.
    """
    return round(mm / 25.4 * ppi)


def get_display_size():

    if DISPLAY_MODE == MODE_1X:

        return (
            TFT_WIDTH,
            TFT_HEIGHT
        )

    elif DISPLAY_MODE == MODE_ZOOM:

        return (
            TFT_WIDTH * ZOOM,
            TFT_HEIGHT * ZOOM
        )

    elif DISPLAY_MODE == MODE_PHYSICAL:

        width = mm_to_pixel(
            TFT_PHYSICAL_WIDTH_MM,
            MONITOR_PPI
        )

        height = mm_to_pixel(
            TFT_PHYSICAL_HEIGHT_MM,
            MONITOR_PPI
        )

        return width, height


# ============================================================
# TFT FRAMEBUFFER
# ============================================================

class TFTDisplay(wx.Panel):

    def __init__(self, parent):

        width, height = get_display_size()

        super().__init__(
            parent,
            size=(width, height)
        )

        self.display_width = width
        self.display_height = height

        self.SetBackgroundStyle(
            wx.BG_STYLE_PAINT
        )

        # ====================================================
        # FRAMEBUFFER
        #
        # SELALU 160 x 80
        # ====================================================

        self.bitmap = wx.Bitmap(
            TFT_WIDTH,
            TFT_HEIGHT,
            depth=32
        )

        self.draw_demo()

        self.Bind(
            wx.EVT_PAINT,
            self.on_paint
        )

    # ========================================================
    # FRAMEBUFFER FUNCTIONS
    # ========================================================

    def clear(self, color):

        dc = wx.MemoryDC()
        dc.SelectObject(self.bitmap)

        dc.SetBackground(
            wx.Brush(wx.Colour(*color))
        )

        dc.Clear()

        dc.SelectObject(
            wx.NullBitmap
        )

    # --------------------------------------------------------

    def draw_pixel(self, x, y, color):

        if not (
            0 <= x < TFT_WIDTH and
            0 <= y < TFT_HEIGHT
        ):
            return

        dc = wx.MemoryDC()
        dc.SelectObject(self.bitmap)

        dc.SetPen(
            wx.Pen(wx.Colour(*color))
        )

        dc.DrawPoint(x, y)

        dc.SelectObject(
            wx.NullBitmap
        )

    # --------------------------------------------------------

    def fill_rect(
        self,
        x,
        y,
        width,
        height,
        color
    ):

        dc = wx.MemoryDC()
        dc.SelectObject(self.bitmap)

        dc.SetPen(wx.TRANSPARENT_PEN)

        dc.SetBrush(
            wx.Brush(wx.Colour(*color))
        )

        dc.DrawRectangle(
            x,
            y,
            width,
            height
        )

        dc.SelectObject(
            wx.NullBitmap
        )

    # --------------------------------------------------------

    def draw_rect(
        self,
        x,
        y,
        width,
        height,
        color
    ):

        dc = wx.MemoryDC()
        dc.SelectObject(self.bitmap)

        dc.SetBrush(
            wx.TRANSPARENT_BRUSH
        )

        dc.SetPen(
            wx.Pen(wx.Colour(*color))
        )

        dc.DrawRectangle(
            x,
            y,
            width,
            height
        )

        dc.SelectObject(
            wx.NullBitmap
        )

    # --------------------------------------------------------

    def draw_text(
        self,
        text,
        x,
        y,
        color,
        size=8
    ):

        dc = wx.MemoryDC()
        dc.SelectObject(self.bitmap)

        font = wx.Font(
            size,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL
        )

        dc.SetFont(font)

        dc.SetTextForeground(
            wx.Colour(*color)
        )

        dc.DrawText(
            text,
            x,
            y
        )

        dc.SelectObject(
            wx.NullBitmap
        )

    # ========================================================
    # DEMO UI
    # ========================================================

    def draw_demo(self):

        self.clear(
            (10, 12, 16)
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        self.fill_rect(
            0,
            0,
            160,
            16,
            (30, 34, 42)
        )

        self.draw_text(
            "T12 SOLDER",
            4,
            2,
            (230, 230, 230),
            8
        )

        # ----------------------------------------------------
        # Temperature
        # ----------------------------------------------------

        self.draw_text(
            "350",
            8,
            25,
            (255, 160, 30),
            20
        )

        self.draw_text(
            "C",
            58,
            34,
            (220, 220, 220),
            8
        )

        # ----------------------------------------------------
        # Set temperature
        # ----------------------------------------------------

        self.draw_text(
            "SET",
            95,
            25,
            (150, 155, 165),
            7
        )

        self.draw_text(
            "350C",
            95,
            34,
            (230, 230, 230),
            8
        )

        # ----------------------------------------------------
        # Power bar
        # ----------------------------------------------------

        self.fill_rect(
            95,
            50,
            55,
            6,
            (45, 48, 55)
        )

        self.fill_rect(
            95,
            50,
            35,
            6,
            (255, 140, 20)
        )

        # ----------------------------------------------------
        # Bottom line
        # ----------------------------------------------------

        self.fill_rect(
            0,
            64,
            160,
            1,
            (60, 65, 75)
        )

        # ----------------------------------------------------
        # Bottom text
        # ----------------------------------------------------

        self.draw_text(
            "T12-K",
            5,
            68,
            (220, 220, 220),
            7
        )

        self.draw_text(
            "READY",
            112,
            68,
            (50, 220, 100),
            7
        )

        self.Refresh(False)

    # ========================================================
    # PAINT
    # ========================================================

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)

        dc.SetBackground(
            wx.Brush(wx.Colour(25, 25, 25))
        )

        dc.Clear()

        # ====================================================
        # MODE 1x
        # ====================================================

        if DISPLAY_MODE == MODE_1X:

            dc.DrawBitmap(
                self.bitmap,
                0,
                0,
                False
            )

            return

        # ====================================================
        # PHYSICAL SIZE
        #
        # Resize 160x80 menjadi ukuran fisik TFT
        # ====================================================

        if DISPLAY_MODE == MODE_PHYSICAL:

            image = self.bitmap.ConvertToImage()

            image = image.Scale(
                self.display_width,
                self.display_height,
                wx.IMAGE_QUALITY_NEAREST
            )

            bitmap = wx.Bitmap(image)

            dc.DrawBitmap(
                bitmap,
                0,
                0,
                False
            )

            return

        # ====================================================
        # ZOOM
        # ====================================================

        if DISPLAY_MODE == MODE_ZOOM:

            image = self.bitmap.ConvertToImage()

            image = image.Scale(
                TFT_WIDTH * ZOOM,
                TFT_HEIGHT * ZOOM,
                wx.IMAGE_QUALITY_NEAREST
            )

            bitmap = wx.Bitmap(image)

            dc.DrawBitmap(
                bitmap,
                0,
                0,
                False
            )


# ============================================================
# MAIN FRAME
# ============================================================

class MainFrame(wx.Frame):

    def __init__(self):

        width, height = get_display_size()

        super().__init__(
            None,
            title="TFT 160x80 Simulator",
            style=wx.DEFAULT_FRAME_STYLE
        )

        self.SetClientSize(
            width,
            height
        )

        self.tft = TFTDisplay(
            self
        )

        self.Centre()


# ============================================================
# APPLICATION
# ============================================================

class TFTSimulator(wx.App):

    def OnInit(self):

        frame = MainFrame()

        frame.Show()

        return True


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app = TFTSimulator(False)

    app.MainLoop()