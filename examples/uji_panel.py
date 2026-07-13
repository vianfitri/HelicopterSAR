import wx

class CustomButton(wx.Panel):
    """Tombol kustom dengan border, sudut melengkung, dan warna latar belakang gelap."""
    def __init__(self, parent, label, icon_text="", bg_color=wx.Colour(20, 35, 60), border_color=wx.Colour(40, 60, 100)):
        super().__init__(parent)
        self.label = label
        self.icon_text = icon_text
        self.bg_color = bg_color
        self.border_color = border_color
        
        self.SetMinSize((150, 50))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClicked)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        width, height = self.GetSize()
        
        # Menggambar latar belakang tombol dengan sudut melengkung (radius 8px)
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.bg_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(self.border_color, 1)))
        gc.DrawRoundedRectangle(1, 1, width - 2, height - 2, 8)
        
        # Menulis Teks/Ikon pada tombol
        gc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.Colour(200, 220, 255))
        
        full_text = f"{self.icon_text}  {self.label}".strip()
        tw, th = gc.GetTextExtent(full_text)
        
        # Posisi teks di tengah-tengah tombol
        gc.DrawText(full_text, (width - tw) / 2, (height - th) / 2)

    def OnClicked(self, event):
        # Tambahkan aksi tombol di sini jika diperlukan
        print(f"Tombol {self.label} diklik!")
        event.Skip()


class HoistCardPanel(wx.Panel):
    """Panel Utama (Card) yang menampung visualisasi Hoist Length."""
    def __init__(self, parent):
        super().__init__(parent)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        self.InitUI()

    def InitUI(self):
        # Main Sizer dengan border/padding luar
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # --- Bagian Atas: Header ---
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Badge angka '2' biru
        # Catatan: Untuk implementasi cepat kita gunakan static text biasa, 
        # namun tata letak aslinya diatur di dalam sizer.
        header_text = wx.StaticText(self, label="2   HOIST LENGTH")
        header_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        header_text.SetForegroundColour(wx.Colour(240, 240, 240))
        
        header_sizer.Add(header_text, 0, wx.ALL, 15)
        main_sizer.Add(header_sizer, 0, wx.EXPAND)
        
        # Spacing untuk area visualisasi tengah (Simulasi gambar helikopter & slider)
        main_sizer.AddSpacer(250) 
        
        # --- Bagian Bawah: Hoist Control ---
        control_title = wx.StaticText(self, label="HOIST CONTROL")
        control_title.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        control_title.SetForegroundColour(wx.Colour(120, 140, 160))
        main_sizer.Add(control_title, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(10)
        
        # Sizer untuk tombol-tombol kontrol
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.btn_retract = CustomButton(self, "RETRACT", "↑", bg_color=wx.Colour(24, 43, 73))
        self.btn_stop = CustomButton(self, "STOP", "Ⅱ", bg_color=wx.Colour(36, 32, 28), border_color=wx.Colour(120, 80, 40))
        self.btn_lower = CustomButton(self, "LOWER", "↓", bg_color=wx.Colour(24, 43, 73))
        
        btn_sizer.Add(self.btn_retract, 1, wx.EXPAND | wx.RIGHT, 10)
        btn_sizer.Add(self.btn_stop, 1, wx.EXPAND | wx.RIGHT, 10)
        btn_sizer.Add(self.btn_lower, 1, wx.EXPAND)
        
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        self.SetSizer(main_sizer)

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        width, height = self.GetSize()
        radius = 16 # Radius kelengkungan card
        header_height = 60 # Tinggi area header
        
        # Warna masing-masing area
        color_header = wx.Colour(20, 32, 55)    # Warna header (lebih terang)
        color_content = wx.Colour(13, 23, 41)   # Warna konten (lebih gelap/sesuai gambar)
        color_border = wx.Colour(30, 45, 70)    # Warna border luar card
        
        # -----------------------------------------------------------------
        # 1. BAGIAN CONTENT (Bawah) & BASE CARD
        # -----------------------------------------------------------------
        # Gambar dulu seluruh background card dengan warna Content
        gc.SetBrush(gc.CreateBrush(wx.Brush(color_content)))
        gc.SetPen(gc.CreatePen(wx.Pen(color_border, 2)))
        gc.DrawRoundedRectangle(1, 1, width - 2, height - 2, radius)
        
        # -----------------------------------------------------------------
        # 2. BAGIAN HEADER (Atas) dengan Warna Berbeda
        # -----------------------------------------------------------------
        # Kita gambar rounded rectangle kecil khusus area atas untuk mengambil kelengkungan atas
        gc.SetBrush(gc.CreateBrush(wx.Brush(color_header)))
        # Hilangkan border pen sementara agar tidak tumpang tindih di dalam
        gc.SetPen(gc.CreatePen(wx.Pen(color_header, 0))) 
        gc.DrawRoundedRectangle(1, 1, width - 2, header_height, radius)
        
        # Karena langkah di atas membuat sudut bawah header ikut melengkung, 
        # kita tutup bagian bawah header dengan kotak persegi (sudut siku-siku) 
        # agar bagian bawah header memotong lurus tepat di garis pembatas.
        gc.DrawRectangle(1, header_height - radius, width - 2, radius)
        
        # -----------------------------------------------------------------
        # 3. GARIS PEMBATAS & PENGATURAN BORDER HEADER
        # -----------------------------------------------------------------
        # Gambar ulang garis border luar khusus untuk area header yang tertimpa tadi
        gc.SetBrush(gc.CreateBrush(wx.TRANSPARENT_BRUSH))
        gc.SetPen(gc.CreatePen(wx.Pen(color_border, 2)))
        gc.DrawRoundedRectangle(1, 1, width - 2, height - 2, radius)
        
        # Gambar Garis Horizontal Pembatas tepat di pertemuan warna (Y = 60)
        divider_pen = wx.Pen(color_border, 1)
        gc.SetPen(gc.CreatePen(divider_pen))
        gc.StrokeLine(2, header_height, width - 2, header_height)
        
        # -----------------------------------------------------------------
        # 4. ORNAMEN HEADER (Badge Angka 2 & Teks)
        # -----------------------------------------------------------------
        # Menggambar badge kotak biru untuk angka "2"
        badge_bg = wx.Colour(30, 80, 190)
        gc.SetBrush(gc.CreateBrush(wx.Brush(badge_bg)))
        gc.SetPen(gc.CreatePen(wx.Pen(badge_bg, 1)))
        gc.DrawRoundedRectangle(20, 18, 24, 24, 4)
        
        # Angka "2"
        gc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.Colour(255, 255, 255))
        gc.DrawText("2", 28, 22)
        
        # Judul "HOIST LENGTH"
        gc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.Colour(240, 240, 240))
        gc.DrawText("HOIST LENGTH", 55, 21)
        
        # -----------------------------------------------------------------
        # 5. DATA PANEL UTAN KANAN (Info 7.42 m)
        # -----------------------------------------------------------------
        info_panel_bg = wx.Colour(17, 30, 54)
        gc.SetBrush(gc.CreateBrush(wx.Brush(info_panel_bg)))
        info_pen = wx.Pen(wx.Colour(25, 40, 70), 1)
        gc.SetPen(gc.CreatePen(info_pen))
        gc.DrawRoundedRectangle(width - 190, 120, 170, 180, 12)
        
        # Teks Info Panel
        gc.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.Colour(120, 140, 170))
        gc.DrawText("HOIST LENGTH", width - 180, 130)
        
        # Angka "7.42 m"
        gc.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.Colour(40, 170, 255))
        gc.DrawText("7.42 m", width - 180, 150)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Hoist Card", size=(450, 600), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.SetBackgroundColour(wx.Colour(10, 15, 25)) # Background luar jendela
        
        # Letakkan card di tengah frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        card = HoistCardPanel(self)
        sizer.Add(card, 1, wx.ALL | wx.EXPAND, 20)
        
        self.SetSizer(sizer)
        self.Center()


if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()