import wx

class CustomHorizontalTrackbar(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(400, 100),
                 min_val=0, max_val=30, value=15, unit="m", style=0):
        super().__init__(parent, id, pos, size, style=style | wx.BORDER_NONE)

        # Nilai Trackbar
        self.min_val = min_val
        self.max_val = max_val
        self.value = max(min_val, min(value, max_val))
        self.unit = unit
        
        # --- KONFIGURASI WARNA & UKURAN ---
        self.bg_color = wx.Colour(20, 30, 45)                 # Latar belakang
        self.main_line_color = wx.Colour(255, 255, 255, 220) # Garis horizontal & siku
        self.tick_color = wx.Colour(200, 200, 200, 180)     # Tick vertical
        self.text_color = wx.Colour(240, 240, 240, 230)     # Teks angka
        self.indicator_color = wx.Colour(245, 120, 20, 255) # Segitiga penunjuk (Orange)
        
        # Glow Color (Orange Gradient)
        self.glow_center_color = wx.Colour(245, 120, 20, 180) 
        self.glow_edge_color = wx.Colour(245, 120, 20, 0)    
        
        # Layout Dimension
        self.tick_count = 25
        self.glow_width = 80   # Lebar efek glow (horizontal)
        self.glow_height = 18  # Tinggi area glow (vertikal)

        # Anti-flicker double buffer
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

        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()

        # Margin & Area Kerja Trackbar
        margin_left = 50
        margin_right = 50
        track_y = h - 35  # Posisi Y garis utama horizontal
        track_width = w - margin_left - margin_right

        # Hitung Posisi X indikator saat ini (Min di Kiri, Max di Kanan)
        val_ratio = (self.value - self.min_val) / float(self.max_val - self.min_val)
        current_x = margin_left + (val_ratio * track_width)

        # -----------------------------------------------------------------
        # 1. Gambar Efek Glow Semi-Transparan (Horizontal Linear Gradient)
        # -----------------------------------------------------------------
        glow_rect_x = current_x - (self.glow_width / 2)
        glow_rect_y = track_y - self.glow_height

        # Gradient dibuat dari posisi tengah (current_x) menyebar ke kiri & kanan
        brush = gc.CreateLinearGradientBrush(
            current_x, glow_rect_y,
            glow_rect_x, glow_rect_y,
            self.glow_center_color, self.glow_edge_color
        )
        gc.SetBrush(brush)
        gc.SetPen(wx.NullPen)
        gc.DrawRectangle(glow_rect_x, glow_rect_y, self.glow_width, self.glow_height)

        # -----------------------------------------------------------------
        # 2. Gambar Tick Line Vertikal
        # -----------------------------------------------------------------
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self.tick_color).Width(1)))
        for i in range(self.tick_count):
            tick_x = margin_left + (i / (self.tick_count - 1)) * track_width
            gc.StrokeLine(tick_x, track_y - 10, tick_x, track_y - 2)

        # -----------------------------------------------------------------
        # 3. Gambar Frame Garis Siku Utama (Bentuk 'U' Tidur)
        # -----------------------------------------------------------------
        path = gc.CreatePath()
        # Siku Kiri sampai Siku Kanan
        path.MoveToPoint(margin_left, track_y - 12)
        path.AddLineToPoint(margin_left, track_y)
        path.AddLineToPoint(margin_left + track_width, track_y)
        path.AddLineToPoint(margin_left + track_width, track_y - 12)

        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self.main_line_color).Width(1.5)))
        gc.SetBrush(wx.NullBrush)
        gc.StrokePath(path)

        # -----------------------------------------------------------------
        # 4. Gambar Segitiga Penunjuk Nilai (Mengarah ke bawah)
        # -----------------------------------------------------------------
        tri_size = 7
        tri_path = gc.CreatePath()
        tri_path.MoveToPoint(current_x, track_y + 3) # Ujung atas segitiga
        tri_path.AddLineToPoint(current_x - tri_size, track_y + 3 + tri_size * 1.5)
        tri_path.AddLineToPoint(current_x + tri_size, track_y + 3 + tri_size * 1.5)
        tri_path.CloseSubpath()

        gc.SetBrush(gc.CreateBrush(wx.Brush(self.indicator_color)))
        gc.SetPen(wx.NullPen)
        gc.FillPath(tri_path)

        # -----------------------------------------------------------------
        # 5. Gambar Teks Nilai (Di Kiri dan Kanan Trackbar)
        # -----------------------------------------------------------------
        font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, self.text_color)

        # Teks Kiri (Min Value)
        text_min = f"{self.min_val} {self.unit}"
        gc.DrawText(text_min, margin_left - 40, track_y - 18)

        # Teks Kanan (Max Value)
        text_max = f"{self.max_val} {self.unit}"
        gc.DrawText(text_max, margin_left + track_width + 10, track_y - 18)

    # -----------------------------------------------------------------
    # Interaksi Mouse Horizontal
    # -----------------------------------------------------------------
    def update_value_from_mouse(self, x_pos):
        w = self.GetClientSize().width
        margin_left = 50
        margin_right = 50
        track_width = w - margin_left - margin_right

        # Clamp posisi mouse ke rentang X trackbar
        clamped_x = max(margin_left, min(x_pos, margin_left + track_width))
        ratio = (clamped_x - margin_left) / track_width

        new_val = int(round(self.min_val + ratio * (self.max_val - self.min_val)))
        if new_val != self.value:
            self.value = new_val
            self.Refresh()

    def on_click(self, event):
        self.is_dragging = True
        self.CaptureMouse()
        self.update_value_from_mouse(event.GetX())

    def on_drag(self, event):
        if self.is_dragging and event.Dragging():
            self.update_value_from_mouse(event.GetX())

    def on_release(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.is_dragging = False


# --- TEST FRAME UNTUK MENAMPILKAN HORIZONTAL TRACKBAR ---
class TestFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Horizontal Custom Trackbar Demo", size=(500, 200))
        self.SetBackgroundColour(wx.Colour(20, 30, 45))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Instance horizontal trackbar
        self.trackbar = CustomHorizontalTrackbar(self, min_val=0, max_val=30, value=15, unit="m")
        
        sizer.Add(self.trackbar, 1, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(sizer)


if __name__ == "__main__":
    app = wx.App(False)
    frame = TestFrame()
    frame.Show()
    app.MainLoop()