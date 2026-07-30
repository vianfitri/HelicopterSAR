import wx

class RoundedCardPanel(wx.Panel):
    """Card Panel dengan sudut melengkung, responsif terhadap resize, 

    serta mendukung pemisah antara Header dan Content Area.
    """
    def __init__(self, parent, title="", value="", bg_color="#FFFFFF", 
                 header_bg="#F8FAFC", border_color="#E2E8F0", radius=12, is_content_card=False):
        super().__init__(parent)
        
        self.bg_color = wx.Colour(bg_color)
        self.header_bg = wx.Colour(header_bg)
        self.border_color = wx.Colour(border_color)
        self.radius = radius
        self.is_content_card = is_content_card
        
        # Buffer untuk mencegah flickering saat resize
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        # Binding Event Paint & Resize (Akomodasi Perubahan Size Window)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        
        # Main Layout Card
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        if self.is_content_card:
            # === MODE 1: CARD CONTENT DENGAN HEADER DIPISAHKAN ===
            
            # Header Container
            header_sizer = wx.BoxSizer(wx.VERTICAL)
            
            lbl_title = wx.StaticText(self, label=title)
            lbl_title.SetForegroundColour(wx.Colour("#1E293B"))
            lbl_title.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            
            header_sizer.Add(lbl_title, 0, wx.ALL, 16)
            self.main_sizer.Add(header_sizer, 0, wx.EXPAND)
            
            # Area Body / Content (Dapat diisi widget lain oleh pengguna)
            self.content_sizer = wx.BoxSizer(wx.VERTICAL)
            
            if value:
                lbl_value = wx.StaticText(self, label=value)
                lbl_value.SetForegroundColour(wx.Colour("#64748B"))
                lbl_value.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                self.content_sizer.Add(lbl_value, 0, wx.ALL, 16)
                
            self.main_sizer.Add(self.content_sizer, 1, wx.EXPAND)
            
        else:
            # === MODE 2: METRIC CARD (RINGKAS) ===
            lbl_title = wx.StaticText(self, label=title)
            lbl_title.SetForegroundColour(wx.Colour("#64748B"))
            lbl_title.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            
            lbl_value = wx.StaticText(self, label=value)
            lbl_value.SetForegroundColour(wx.Colour("#0F172A"))
            lbl_value.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            
            self.main_sizer.Add(lbl_title, 0, wx.LEFT | wx.RIGHT | wx.TOP, 16)
            self.main_sizer.Add(lbl_value, 0, wx.ALL, 16)
        
        self.SetSizer(self.main_sizer)

    def on_size(self, event):
        """Memastikan canvas dikaji ulang setiap kali ukuran window berubah."""
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        """Draw background, rounded borders, dan garis pemisah header secara dinamis."""
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            width, height = self.GetClientSize()
            if width <= 0 or height <= 0:
                return

            # 1. Gambar Background Utama Card (dengan Rounded Corners)
            card_path = gc.CreatePath()
            card_path.AddRoundedRectangle(1, 1, width - 2, height - 2, self.radius)
            
            gc.SetBrush(gc.CreateBrush(wx.Brush(self.bg_color)))
            gc.SetPen(gc.CreatePen(wx.Pen(self.border_color, 1)))
            gc.DrawPath(card_path)
            
            # 2. Gambar Header terpisah jika Mode Content Card aktif
            if self.is_content_card:
                header_height = 48  # Tinggi area header
                
                # Clipper agar background header tidak keluar dari sudut rounded atas
                gc.Clip(card_path)
                
                # Background khusus Header
                header_rect = gc.CreatePath()
                header_rect.AddRectangle(0, 0, width, header_height)
                gc.SetBrush(gc.CreateBrush(wx.Brush(self.header_bg)))
                gc.SetPen(gc.CreatePen(wx.Pen(wx.Colour(0, 0, 0, 0)))) # Tanpa pen/border
                gc.DrawPath(header_rect)
                
                # Garis Pemisah (Divider Line) antara Header & Body
                divider_path = gc.CreatePath()
                divider_path.MoveToPoint(0, header_height)
                divider_path.AddLineToPoint(width, header_height)
                gc.SetPen(gc.CreatePen(wx.Pen(self.border_color, 1)))
                gc.DrawPath(divider_path)
                
                gc.ResetClip()


class DashboardFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Responsive Dashboard wxPython", size=(1000, 650))
        self.SetMinSize((700, 500))  # Mencegah layout rusak jika window terlalu kecil
        
        self.SetBackgroundColour(wx.Colour("#F1F5F9"))
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 1. Title Header Dashboard
        header_text = wx.StaticText(self, label="Executive Dashboard")
        header_text.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        header_text.SetForegroundColour(wx.Colour("#0F172A"))
        main_sizer.Add(header_text, 0, wx.ALL, 24)
        
        # 2. Grid Cards (Menggunakan GridSizer agar proporsional saat di-resize)
        card_grid = wx.GridSizer(rows=1, cols=4, gap=(16, 16))
        
        cards_data = [
            {"title": "TOTAL REVENUE", "value": "$45,231"},
            {"title": "ACTIVE USERS", "value": "1,205"},
            {"title": "NEW ORDERS", "value": "354"},
            {"title": "CONVERSION RATE", "value": "3.2%"}
        ]
        
        for data in cards_data:
            card = RoundedCardPanel(
                self, 
                title=data["title"], 
                value=data["value"],
                radius=10
            )
            card_grid.Add(card, 1, wx.EXPAND)
            
        main_sizer.Add(card_grid, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 24)
        
        # 3. Content Card Utama (Header & Content Dipisahkan)
        content_card = RoundedCardPanel(
            self, 
            title="ANALYTICS OVERVIEW", 
            value="Area ini fleksibel. Anda dapat menambahkan Grafik (Matplotlib/wxPyPlot), Tabel, atau Form di sini.", 
            bg_color="#FFFFFF",
            header_bg="#F8FAFC",  # Warna beda pada background header
            border_color="#CBD5E1",
            radius=12,
            is_content_card=True
        )
        
        # Memastikan Content Card fleksibel membesar menyerap sisa space vertikal
        main_sizer.Add(content_card, 1, wx.ALL | wx.EXPAND, 24)
        
        self.SetSizer(main_sizer)
        self.Center()


if __name__ == "__main__":
    app = wx.App()
    frame = DashboardFrame()
    frame.Show()
    app.MainLoop()