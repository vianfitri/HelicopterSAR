import wx

class LongitudinalPosControl(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=(220, 80), 
                 val=0.0, corner_radius=15, 
                 bg_color=wx.Colour(30, 41, 59),      # Slate dark
                 border_color=wx.Colour(56, 189, 248), # Sky blue
                 text_color=wx.Colour(241, 245, 249),  # Near white
                 label_color=wx.Colour(148, 163, 184)): # Muted text
        
        super().__init__(parent, id, pos, size, style=wx.BORDER_NONE | wx.FULL_REPAINT_ON_RESIZE)
        
        self.value = val
        self.corner_radius = corner_radius
        self.bg_color = bg_color
        self.border_color = border_color
        self.text_color = text_color
        self.label_color = label_color
        
        # Mencegah flicker pada beberapa sistem
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        # Event binding
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None) # Abaikan erase bg agar transparan lancar

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        # Dapatkan GraphicsContext dari DC untuk dukungan Anti-Aliasing & Alpha Transparency
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return
            
        w, h = self.GetClientSize()
        
        # Offset 1px agar garis border 2px tidak terpotong di tepi control
        border_thickness = 2
        offset = border_thickness / 2.0
        rect_x = offset
        rect_y = offset
        rect_w = w - border_thickness
        rect_h = h - border_thickness
        
        # 1. Gambar Background Rounded Rectangle
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.bg_color)))
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self.border_color).Width(border_thickness)))
        
        # Path untuk rounded rectangle
        path = gc.CreatePath()
        path.AddRoundedRectangle(rect_x, rect_y, rect_w, rect_h, self.corner_radius)
        
        # Fill dan Stroke (Border) sekaligus
        gc.DrawPath(path)
        
        # 2. Gambar Teks (Label Header & Nilai Position)
        # Font untuk Label
        label_font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(gc.CreateFont(label_font, self.label_color))
        
        label_str = "LONGITUDINAL POS"
        lw, lh = gc.GetTextExtent(label_str)
        # Posisi label di bagian atas tengah
        gc.DrawText(label_str, (w - lw) / 2, 12)
        
        # Font untuk Nilai Utama
        val_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(gc.CreateFont(val_font, self.text_color))
        
        val_str = f"{self.value:+.2f} m"  # Format 2 desimal dengan tanda +/-
        vw, vh = gc.GetTextExtent(val_str)
        # Posisi nilai di bagian tengah-bawah
        gc.DrawText(val_str, (w - vw) / 2, 34)

    def SetValue(self, val):
        """Method untuk memperbarui nilai posisi secara dinamis"""
        if self.value != val:
            self.value = val
            self.Refresh()  # Pemicu repaint

    def GetValue(self):
        return self.value


# ============================================================================
# Contoh Penggunaan / Testing Frame
# ============================================================================
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Control Test", size=(400, 300))
        
        # Panel utama diberi warna latar gradien/berbeda untuk membuktikan transparansi sudut
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(238, 242, 255)) # Soft Indigo Background
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Label instruksi
        info_text = wx.StaticText(panel, label="Area luar sudut control transparan terhadap panel ini:")
        sizer.Add(info_text, 0, wx.ALL | wx.ALIGN_CENTER, 15)
        
        # Instantiate Custom Control
        self.long_ctrl = LongitudinalPosControl(panel, val=12.45)
        sizer.Add(self.long_ctrl, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        # Slider untuk mencoba mengubah nilai secara live
        self.slider = wx.Slider(panel, value=1245, minValue=-5000, maxValue=5000, style=wx.SL_HORIZONTAL)
        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderChange)
        sizer.Add(self.slider, 0, wx.EXPAND | wx.ALL, 20)
        
        panel.SetSizer(sizer)
        self.Centre()

    def OnSliderChange(self, event):
        val = self.slider.GetValue() / 100.0
        self.long_ctrl.SetValue(val)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()