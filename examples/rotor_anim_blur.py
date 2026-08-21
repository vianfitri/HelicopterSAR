import math
import wx

class HelicopterRotorCanvas(wx.Panel):
    def __init__(self, parent, frame_count=8, speed_ms=30):
        super().__init__(parent)
        
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.frame_count = frame_count
        self.current_frame = 0
        
        # Load aset dasar (pastikan file PNG transparan)
        # Jika tidak ada file, kode ini membuat gambar rotor sintetis transparan
        self.base_rotor_image = self._create_dummy_rotor_image()
        
        # Pre-render semua frame rotasi ke dalam RAM
        self.rotated_bitmaps = self._pre_render_rotations()
        
        # Timer untuk animasi
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        
        self.timer.Start(speed_ms)

    def _create_dummy_rotor_image(self):
        """Membuat gambar rotor transparan dengan sedikit efek blur alpha."""
        img = wx.Image(200, 200, clear=True)
        img.InitAlpha()
        
        # Menggunakan wx.GraphicsContext untuk menggambar baling-baling transparan
        bmp = wx.Bitmap(img)
        dc = wx.MemoryDC(bmp)
        gc = wx.GraphicsContext.Create(dc)
        
        if gc:
            # Baling-baling utama (semi-transparan untuk efek blur)
            gc.SetBrush(wx.Brush(wx.Colour(50, 50, 50, 180)))
            gc.CreatePath()
            gc.DrawEllipse(10, 95, 180, 10)
            
            # Efek jejak blur (alpha lebih rendah)
            gc.SetBrush(wx.Brush(wx.Colour(100, 100, 100, 80)))
            gc.DrawEllipse(15, 85, 170, 30)
            
            # Poros tengah
            gc.SetBrush(wx.Brush(wx.Colour(200, 0, 0, 255)))
            gc.DrawEllipse(90, 90, 20, 20)
            
        dc.SelectObject(wx.NullBitmap)
        return bmp.ConvertToImage()

    def _pre_render_rotations(self):
        """Memutar gambar di awal dan menyimpan hasilnya dalam bentuk wx.Bitmap."""
        bitmaps = []
        center = wx.Point2D(self.base_rotor_image.GetWidth() / 2, 
                            self.base_rotor_image.GetHeight() / 2)
        
        angle_step = (2 * math.pi) / self.frame_count
        
        for i in range(self.frame_count):
            angle = i * angle_step
            # Rotasi cepat via wx.Image
            rotated_img = self.base_rotor_image.Rotate(angle, center, interpolate=True)
            bitmaps.append(wx.Bitmap(rotated_img))
            
        return bitmaps

    def on_timer(self, event):
        # Ganti indeks frame
        self.current_frame = (self.current_frame + 1) % self.frame_count
        self.Refresh(False)  # Trigger paint event tanpa menghapus background

    def on_paint(self, event):
        # Gunakan AutoBufferedPaintDC agar animasi halus tanpa flickering
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(240, 240, 240)))
        dc.Clear()
        
        # Gambar frame rotor yang sudah di-cache
        bmp = self.rotated_bitmaps[self.current_frame]
        
        # Posisikan di tengah kanvas
        w, h = self.GetClientSize()
        x = (w - bmp.GetWidth()) // 2
        y = (h - bmp.GetHeight()) // 2
        
        dc.DrawBitmap(bmp, x, y, True)  # True = aktifkan alpha channel

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Animasi Rotor Helikopter", size=(400, 400))
        HelicopterRotorCanvas(self)

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()