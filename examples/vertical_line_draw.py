import wx

class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Koordinat tetap titik awal (atas)
        self.start_x = 200
        self.start_y = 50
        
        # Panjang awal garis
        self.line_length = 100
        
        # Menggunakan ikon standar dari sistem (Bisa diganti dengan wx.Bitmap('path/ke/icon.png'))
        self.icon = wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_OTHER, (32, 32))
        
        # Bind event paint untuk menggambar
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

    def set_line_length(self, length):
        self.line_length = length
        self.Refresh()  # Memicu pemanggilan EVT_PAINT ulang

    def on_paint(self, event):
        # Menggunakan AutoBufferedPaintDC untuk mencegah flicker saat slider digeser
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        
        # 1. Hitung titik ujung bawah garis
        end_x = self.start_x
        end_y = self.start_y + self.line_length
        
        # 2. Gambar garis vertikal
        dc.SetPen(wx.Pen(wx.Colour(0, 102, 204), 4))  # Warna biru, tebal 4px
        dc.DrawLine(self.start_x, self.start_y, end_x, end_y)
        
        # 3. Gambar titik awal (opsional, untuk indikator visual)
        dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0)))
        dc.DrawCircle(self.start_x, self.start_y, 5)
        
        # 4. Gambar ikon tepat menempel di ujung bawah garis
        if self.icon.IsOk():
            icon_w = self.icon.GetWidth()
            icon_h = self.icon.GetHeight()
            
            # Posisikan ikon agar berada simetris di tengah ujung bawah garis
            icon_x = end_x - (icon_w // 2)
            icon_y = end_y  # Menempel langsung di bawah ujung garis
            
            dc.DrawBitmap(self.icon, icon_x, icon_y, True)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Garis Vertikal Dinamis dengan Slider", size=(600, 500))
        
        panel = wx.Panel(self)
        
        # 1. Buat Canvas khusus untuk menggambar
        self.canvas = CanvasPanel(panel)
        
        # 2. Buat Vertical Slider Control
        # wx.SL_VERTICAL = slider berbentuk vertikal
        # wx.SL_INVERSE  = nilai bertambah saat slider digeser ke bawah
        self.slider = wx.Slider(
            panel, 
            value=100, 
            minValue=20, 
            maxValue=300, 
            style=wx.SL_VERTICAL | wx.SL_INVERSE | wx.SL_LABELS
        )
        
        # Bind event slider saat nilainya berubah
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider_change)
        
        # 3. Tata letak menggunakan Sizer
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Tambahkan canvas (mengisi area utama)
        main_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 10)
        
        # Tambahkan slider di sebelah kanan
        main_sizer.Add(self.slider, 0, wx.EXPAND | wx.ALL, 10)
        
        panel.SetSizer(main_sizer)
        self.Centre()
        

    def on_slider_change(self, event):
        val = self.slider.GetValue()
        self.canvas.set_line_length(val)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()