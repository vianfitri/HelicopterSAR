import wx
import os

class Canvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Load gambar
        self.imageScale = 0.2
        image = wx.Image("examples/images/bell412pps.png")
        self.bitmap = wx.Bitmap(image)

        # Posisi gambar
        self.pos_x = 100
        self.pos_y = 100

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        # Gambar selalu berada di tengah secara vertikal
        self.pos_y = (
            self.GetClientSize().height - self.bitmap.GetHeight()
        ) // 2

        self.Refresh()
        event.Skip()

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        width, height = self.GetClientSize()

        # Background
        gc.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
        gc.DrawRectangle(0, 0, width, height)

        # Garis lintasan
        gc.SetPen(wx.Pen(wx.Colour(180, 180, 180), 2))
        gc.StrokeLine(
            20,
            height // 2,
            width - 20,
            height // 2
        )

        # Gambar helicopter
        gc.DrawBitmap(
            self.bitmap,
            self.pos_x,
            self.pos_y,
            self.bitmap.GetWidth() * self.imageScale,
            self.bitmap.GetHeight() * self.imageScale
        )


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title="GraphicsContext Demo", size=(900, 500))

        panel = wx.Panel(self)

        self.canvas = Canvas(panel)

        self.slider = wx.Slider(
            panel,
            minValue=0,
            maxValue=700,
            value=100,
            style=wx.SL_HORIZONTAL | wx.SL_INVERSE
        )

        self.slider.Bind(wx.EVT_SLIDER, self.on_slider)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.slider, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(sizer)

    def on_slider(self, event):
        self.canvas.pos_x = self.slider.GetValue()
        self.canvas.Refresh()


class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = App(False)
    app.MainLoop()