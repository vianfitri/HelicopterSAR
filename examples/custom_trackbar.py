import wx

class CustomTrackbar(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(100, 400),
                 min_val=0, max_val=30, value=15, unit="m", style=0):
        super().__init__(parent, id, pos, size, style=style | wx.BORDER_NONE)

        # Nilai Trackbar
        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min_val, min(value, max_val))
        self.unit = unit
        
        # --- KONFIGURASI WARNA & UKURAN (Bisa Diubah Sesuai Kebutuhan) ---
        self.bg_color = wx.Colour(20, 30, 45)         # Warna latar belakang simulator
        self.main_line_color = wx.Colour(255, 255, 255, 220) # Warna garis vertikal & siku
        self.tick_color = wx.Colour(200, 200, 200, 180)     # Warna tick horizontal
        self.text_color = wx.Colour(240, 240, 240, 230)     # Warna teks angka
        self.indicator_color = wx.Colour(245, 120, 20, 255) # Warna segitiga penunjuk (Orange)
        
        # Warna Glow Semi-Transparan (Orange Gradient)
        self.glow_center_color = wx.Colour(245, 120, 20, 180) 
        self.glow_edge_color = wx.Colour(245, 120, 20, 0)    
        
        # Dimensional Layout
        self.tick_count = 25
        self.glow_height = 80  # Tinggi efek glow dalam piksel
        self.glow_width = 18   # Lebar area glow

        # Double Buffering untuk mencegah flickering saat dragging
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Bind Event
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_LEFT_UP, self.on_release)
        self.Bind(wx.EVT_MOTION, self.on_drag)

        self.is_dragging = False

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.bg_color))
        dc.Clear()

        # Gunakan GraphicsContext untuk mendukung Alpha/Transparansi & Anti-Aliasing
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()

        # Margin & Area Kerja Trackbar
        margin_top = 25
        margin_bottom = 25
        track_x = w - 45  # Posisi X garis vertikal utama
        track_height = h - margin_top - margin_bottom

        # Hitung Posisi Y indikator saat ini (0 di atas, Max di bawah)
        val_ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
        current_y = margin_top + (val_ratio * track_height)

        # -----------------------------------------------------------------
        # 1. Gambar Efek Glow Semi-Transparan (Linear Gradient)
        # -----------------------------------------------------------------
        glow_rect_y = current_y - (self.glow_height / 2)
        glow_rect_x = track_x - self.glow_width

        # Buat Gradient Radial/Linear dari tengah glow ke batas atas-bawah
        brush = gc.CreateLinearGradientBrush(
            glow_rect_x, current_y,
            glow_rect_x, glow_rect_y,
            self.glow_center_color, self.glow_edge_color
        )
        gc.SetBrush(brush)
        gc.SetPen(wx.NullPen)
        gc.DrawRectangle(glow_rect_x, glow_rect_y, self.glow_width, self.glow_height)

        # -----------------------------------------------------------------
        # 2. Gambar Tick Line Horizontal
        # -----------------------------------------------------------------
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self.tick_color).Width(1)))
        for i in range(self.tick_count):
            tick_y = margin_top + (i / (self.tick_count - 1)) * track_height
            gc.StrokeLine(track_x - 10, tick_y, track_x - 2, tick_y)

        # -----------------------------------------------------------------
        # 3. Gambar Frame Garis Siku Utama (Bentuk 'L' atas dan bawah)
        # -----------------------------------------------------------------
        path = gc.CreatePath()
        # Siku Atas
        path.MoveToPoint(track_x - 12, margin_top)
        path.AddLineToPoint(track_x, margin_top)
        path.AddLineToPoint(track_x, margin_top + track_height)
        path.AddLineToPoint(track_x - 12, margin_top + track_height)

        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self.main_line_color).Width(1.5)))
        gc.SetBrush(wx.NullBrush)
        gc.StrokePath(path)

        # -----------------------------------------------------------------
        # 4. Gambar Segitiga Penunjuk Nilai (Indicator)
        # -----------------------------------------------------------------
        tri_size = 7
        tri_path = gc.CreatePath()
        tri_path.MoveToPoint(track_x + 3, current_y)  # Ujung kiri segitiga
        tri_path.AddLineToPoint(track_x + 3 + tri_size * 1.5, current_y - tri_size)
        tri_path.AddLineToPoint(track_x + 3 + tri_size * 1.5, current_y + tri_size)
        tri_path.CloseSubpath()

        gc.SetBrush(gc.CreateBrush(wx.Brush(self.indicator_color)))
        gc.SetPen(wx.NullPen)
        gc.FillPath(tri_path)

        # -----------------------------------------------------------------
        # 5. Gambar Teks Nilai (Ujung Atas & Bawah)
        # -----------------------------------------------------------------
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, self.text_color)

        # Teks Atas
        text_top = f"{self.min_val} {self.unit}"
        gc.DrawText(text_top, track_x - 45, margin_top - 8)

        # Teks Bawah
        text_bottom = f"{self.max_val} {self.unit}"
        gc.DrawText(text_bottom, track_x - 48, margin_top + track_height - 8)

    # -----------------------------------------------------------------
    # Interaksi Mouse (Click & Drag)
    # -----------------------------------------------------------------
    def update_value_from_mouse(self, y_pos):
        h = self.GetClientSize().height
        margin_top = 25
        margin_bottom = 25
        track_height = h - margin_top - margin_bottom

        # Clamp posisi mouse ke area trackbar
        clamped_y = max(margin_top, min(y_pos, margin_top + track_height))
        ratio = (clamped_y - margin_top) / track_height

        # Rekalkulasi nilai integer
        new_val = int(round(self.min_val + ratio * (self.max_val - self.min_val)))
        if new_val != self.value:
            self.value = new_val
            self.Refresh() # Redraw widget

    def on_click(self, event):
        self.is_dragging = True
        self.CaptureMouse()
        self.update_value_from_mouse(event.GetY())

    def on_drag(self, event):
        if self.is_dragging and event.Dragging():
            self.update_value_from_mouse(event.GetY())

    def on_release(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.is_dragging = False


# --- TEST FRAME UNTUK MENAMPILKAN TRACKBAR ---
class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Trackbar Demo", size=(300, 500))
        self.SetBackgroundColour(wx.Colour(20, 30, 45)) # Gelap agar efek glow terlihat

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Instance custom trackbar
        self.trackbar = CustomTrackbar(self, min_val=0, max_val=30, value=18, unit="m")
        
        sizer.Add(self.trackbar, 1, wx.ALIGN_CENTER | wx.ALL, 20)
        self.SetSizer(sizer)


if __name__ == "__main__":
    app = wx.App(False)
    frame = TestFrame()
    frame.Show()
    app.MainLoop()