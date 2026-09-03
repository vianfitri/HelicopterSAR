import wx

class CustomPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        
        if not gc:
            return

        # Parameter Utama
        x, y = 20, 20
        width, height = 200, 100
        radius = 15
        
        # 1. Gambar Area Utama (Fill) & Border Utama (Misal: Abu-abu)
        gc.SetBrush(wx.Brush(wx.Colour(240, 240, 240))) # Warna Background
        gc.SetPen(wx.Pen(wx.Colour(200, 200, 200), 2))   # Warna Border Utama
        gc.DrawRoundedRectangle(x, y, width, height, radius)

        # 2. Buat Path Khusus untuk Garis Sisi Kiri
        path = gc.CreatePath()
        
        # Mulai dari sudut kanan atas lengkungan kiri-bawah (titik bawah sisi kiri)
        path.MoveToPoint(x, y + height - radius)
        
        # Tarik garis lurus ke atas sepanjang sisi kiri
        path.AddLineToPoint(x, y + radius)
        
        # Gambar lengkungan sudut kiri-atas
        # Arc(x, y, radius, startAngle, endAngle, clockwise)
        # pi = sudut 180 deg (kiri), 1.5 * pi = sudut 270 deg (atas)
        import math
        path.AddArc(x + radius, y + radius, radius, math.pi, 1.5 * math.pi, True)

        # 3. Gambar Garis Sisi Kiri dengan Warna Berbeda (Misal: Biru)
        left_border_color = wx.Colour(0, 120, 215)
        border_width = 5
        
        gc.SetPen(wx.Pen(left_border_color, border_width))
        gc.StrokePath(path)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Rounded Rectangle", size=(300, 200))
        CustomPanel(self)

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()