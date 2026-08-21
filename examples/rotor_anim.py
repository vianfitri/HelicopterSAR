import wx

class HelicopterCanvas(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT) # Mencegah flickering
        
        # 1. Buat Aset Gambar Transparan secara Programatis (Ganti dengan file PNG Anda jika ada)
        self.rotor_image = self.create_dummy_blurred_rotor()
        
        # State animasi
        self.angle = 0.0
        
        # 2. Timer Animasi (~60 FPS)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(16) # 16ms = ~60 FPS
        
        # Event binding untuk rendering
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def create_dummy_blurred_rotor(self):
        """
        Membuat gambar bitmap transparan sederhana dengan efek blur/translucency
        sebagai pengganti file PNG eksternal.
        """
        size = 200
        bmp = wx.Bitmap(size, size, 32)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0, 0))) # Fully transparent background
        dc.Clear()
        
        # Gambar bayangan bilah rotor (seperti efek motion blur)
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            # Lingkaran blur samar di area putaran
            gc.SetBrush(
                gc.CreateRadialGradientBrush(
                    100,
                    100,
                    100,
                    100,
                    100,
                    wx.Colour(50, 50, 50, 40),
                    wx.Colour(200, 200, 200, 0)
               )
            )
            gc.DrawEllipse(10, 10, 180, 180)
            
            # Bilah utama transparan
            gc.SetBrush(wx.Brush(wx.Colour(30, 30, 30, 180)))
            gc.DrawRectangle(15, 93, 170, 14)
            gc.DrawRectangle(93, 15, 14, 170)
            
            # Hub tengah rotor
            gc.SetBrush(wx.Brush(wx.Colour(100, 100, 100, 255)))
            gc.DrawEllipse(85, 85, 30, 30)

        dc.SelectObject(wx.NullBitmap)
        return bmp.ConvertToImage()

    def on_timer(self, event):
        # Update sudut putaran (tambah nilai untuk mempercepat)
        self.angle = (self.angle + 25.0) % 360.0
        self.Refresh(False) # Request redraw tanpa menghapus background

    def on_size(self, event):
        self.Refresh(False)
        event.Skip()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(135, 206, 235))) # Warna langit/background
        dc.Clear()

        # Konversi wx.Image ke wx.Bitmap setelah diputar
        # wx.Image.Rotate menerima sudut dalam Radian
        radians = self.angle * (3.14159 / 180.0)
        
        # Putar gambar terhadap titik pusat (100, 100)
        rotated_img = self.rotor_image.Rotate(
            radians, 
            rotationCentre=wx.Point(100, 100), 
            interpolating=True
        )
        
        rotated_bmp = wx.Bitmap(rotated_img)

        # Gambar di tengah panel
        w, h = self.GetClientSize()
        bw, bh = rotated_bmp.GetSize()
        x = (w - bw) // 2
        y = (h - bh) // 2

        dc.DrawBitmap(rotated_bmp, x, y, True)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Animasi Rotor Helikopter", size=(400, 400))
        HelicopterCanvas(self)
        self.Center()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()