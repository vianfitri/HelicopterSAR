import wx


# ============================================================
# TFT RESOLUTION
# ============================================================

TFT_WIDTH = 160
TFT_HEIGHT = 80


# ============================================================
# TFT DISPLAY
# ============================================================

class TFTDisplay(wx.Panel):

    def __init__(self, parent):
        super().__init__(
            parent,
            size=(TFT_WIDTH, TFT_HEIGHT)
        )

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Framebuffer TFT sebenarnya: 160 x 80
        self.bitmap = wx.Bitmap(
            TFT_WIDTH,
            TFT_HEIGHT,
            depth=32
        )

        self.draw_screen()

        self.Bind(wx.EVT_PAINT, self.on_paint)

    # --------------------------------------------------------
    # DRAW TFT
    # --------------------------------------------------------

    def draw_screen(self):

        dc = wx.MemoryDC()
        dc.SelectObject(self.bitmap)

        # Background
        dc.SetBackground(
            wx.Brush(wx.Colour(10, 12, 16))
        )
        dc.Clear()

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(
            wx.Brush(wx.Colour(30, 34, 42))
        )

        dc.DrawRectangle(
            0, 0,
            160, 16
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        font = wx.Font(
            8,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        )

        dc.SetFont(font)
        dc.SetTextForeground(
            wx.Colour(230, 230, 230)
        )

        dc.DrawText(
            "T12 SOLDER",
            4,
            3
        )

        # ----------------------------------------------------
        # STATUS LED
        # ----------------------------------------------------

        dc.SetBrush(
            wx.Brush(wx.Colour(40, 210, 90))
        )

        dc.DrawCircle(
            145,
            8,
            3
        )

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        font = wx.Font(
            20,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        )

        dc.SetFont(font)

        dc.SetTextForeground(
            wx.Colour(255, 160, 30)
        )

        dc.DrawText(
            "350",
            7,
            25
        )

        # Celsius
        font = wx.Font(
            8,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL
        )

        dc.SetFont(font)

        dc.SetTextForeground(
            wx.Colour(220, 220, 220)
        )

        dc.DrawText(
            "°C",
            58,
            35
        )

        # ----------------------------------------------------
        # SET TEMP
        # ----------------------------------------------------

        dc.SetTextForeground(
            wx.Colour(150, 155, 165)
        )

        dc.DrawText(
            "SET",
            92,
            25
        )

        dc.SetTextForeground(
            wx.Colour(230, 230, 230)
        )

        dc.DrawText(
            "350°C",
            92,
            34
        )

        # ----------------------------------------------------
        # POWER BAR
        # ----------------------------------------------------

        dc.SetBrush(
            wx.Brush(wx.Colour(45, 48, 55))
        )

        dc.DrawRectangle(
            92,
            50,
            58,
            6
        )

        dc.SetBrush(
            wx.Brush(wx.Colour(255, 140, 20))
        )

        dc.DrawRectangle(
            92,
            50,
            38,
            6
        )

        # ----------------------------------------------------
        # BOTTOM LINE
        # ----------------------------------------------------

        dc.SetPen(
            wx.Pen(wx.Colour(55, 60, 70))
        )

        dc.DrawLine(
            0,
            64,
            159,
            64
        )

        # ----------------------------------------------------
        # BOTTOM INFORMATION
        # ----------------------------------------------------

        dc.SetTextForeground(
            wx.Colour(130, 135, 145)
        )

        dc.DrawText(
            "TIP",
            4,
            68
        )

        dc.SetTextForeground(
            wx.Colour(230, 230, 230)
        )

        dc.DrawText(
            "T12-K",
            27,
            68
        )

        dc.SetTextForeground(
            wx.Colour(50, 220, 100)
        )

        dc.DrawText(
            "READY",
            113,
            68
        )

        dc.SelectObject(wx.NullBitmap)

    # --------------------------------------------------------
    # PAINT
    # --------------------------------------------------------

    def on_paint(self, event):

        dc = wx.PaintDC(self)

        # ====================================================
        # INI YANG PALING PENTING
        #
        # Tidak ada:
        #   Scale()
        #   Stretch()
        #   Resize()
        #
        # Bitmap 160x80 digambar 160x80.
        #
        # 1 pixel bitmap = 1 pixel monitor
        # ====================================================

        dc.DrawBitmap(
            self.bitmap,
            0,
            0,
            False
        )


# ============================================================
# MAIN FRAME
# ============================================================

class MainFrame(wx.Frame):

    def __init__(self):

        # ----------------------------------------------------
        # NO TITLE BAR
        # NO BORDER
        # ----------------------------------------------------

        super().__init__(
            None,
            title="TFT 160x80",
            style=wx.FRAME_NO_TASKBAR |
                  wx.BORDER_NONE
        )

        # Frame client = 160x80
        self.SetClientSize(
            TFT_WIDTH,
            TFT_HEIGHT
        )

        # TFT
        self.tft = TFTDisplay(self)

        self.SetSize(
            TFT_WIDTH,
            TFT_HEIGHT
        )

        # Posisi di tengah layar
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