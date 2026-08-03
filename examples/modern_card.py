import wx

class ModernCard(wx.Control):
    """
    Komponen Custom Card Reusable untuk wxPython.
    Memiliki border melengkung, shadow halus, title, dan area konten khusus.
    """
    def __init__(self, parent, id=wx.ID_ANY, title="Card Title", 
                 bg_color="#FFFFFF", border_color="#E0E0E0", 
                 title_color="#212121", line_color="#EEEEEE",
                 corner_radius=12, title_font=None, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        
        # Menggunakan wx.TRANSPARENT_WINDOW agar area luar corner transparan terhadap parent
        super().__init__(parent, id, pos=pos, size=size, style=style | wx.TRANSPARENT_WINDOW)

        # Config Parameter
        self._title = title
        self._bg_color = wx.Colour(bg_color)
        self._border_color = wx.Colour(border_color)
        self._title_color = wx.Colour(title_color)
        self._line_color = wx.Colour(line_color)
        self._corner_radius = corner_radius
        self._title_font = title_font or wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # Internal Padding & Dimension Metrics
        self._padding = 16
        self._title_height = 40
        self._shadow_size = 6  # Space untuk efek bayangan di luar card

        # Sizer utama komponen (Card Control)
        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Space kosong atas (Padding + Title Height)
        self._main_sizer.AddSpacer(self._title_height + self._padding)
        
        # Container Sizer khusus tempat menampung widget anak (Content Area)
        self._content_sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_sizer.Add(self._content_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, self._padding)
        
        self.SetSizer(self._main_sizer)

        # Event Bindings
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)  # Mencegah flicker

    def GetContentSizer(self):
        """Mengembalikan sizer area konten agar widget luar bisa dimasukkan ke dalam card."""
        return self._content_sizer

    def AddContent(self, widget, proportion=0, flag=wx.EXPAND, border=0):
        """Helper praktis untuk menambahkan widget langsung ke area konten card."""
        self._content_sizer.Add(widget, proportion, flag, border)
        self.Layout()

    def _on_paint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
        width, height = self.GetSize()

        # Margin offset untuk memberi ruang rendering shadow di luar border card
        s = self._shadow_size
        card_x = s
        card_y = s
        card_w = width - (2 * s)
        card_h = height - (2 * s)

        # 1. Gambar Soft Drop Shadow di sekeliling card
        shadow_path = gc.CreatePath()
        shadow_path.AddRoundedRectangle(card_x, card_y + 2, card_w, card_h, self._corner_radius)
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 15)))) # Black transparan
        gc.SetPen(wx.NullPen)
        gc.FillPath(shadow_path)

        # 2. Gambar Background Utama Card
        card_path = gc.CreatePath()
        card_path.AddRoundedRectangle(card_x, card_y, card_w, card_h, self._corner_radius)
        gc.SetBrush(gc.CreateBrush(wx.Brush(self._bg_color)))
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self._border_color).Width(1)))
        gc.DrawPath(card_path)

        # 3. Gambar Text Title
        gc.SetFont(self._title_font, self._title_color)
        text_x = card_x + self._padding
        text_y = card_y + (self._title_height // 2) - 8
        gc.DrawText(self._title, text_x, text_y)

        # 4. Gambar Border Pembatas + Soft Line Shadow di Bawah Title
        line_y = card_y + self._title_height
        
        # Soft Shadow Line (Bayangan halus di bawah garis)
        line_shadow_path = gc.CreatePath()
        line_shadow_path.MoveToPoint(card_x + 1, line_y + 1)
        line_shadow_path.AddLineToPoint(card_x + card_w - 1, line_y + 1)
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(0, 0, 0, 10)).Width(2)))
        gc.StrokePath(line_shadow_path)

        # Garis Pembatas Utama (Subtle Border)
        line_path = gc.CreatePath()
        line_path.MoveToPoint(card_x + 1, line_y)
        line_path.AddLineToPoint(card_x + card_w - 1, line_y)
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self._line_color).Width(1)))
        gc.StrokePath(line_path)

# ----------------------------------------------------------------------
# CONTOH PENGGUNAAN / DEMO APPLICATION
# ----------------------------------------------------------------------
class DemoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Modern Card Demo", size=(800, 500))
        
        # Panel utama diberi background berwarna untuk membuktikan transparansi corner
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#F4F6F9")

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Card 1: Tema Terang (Light Mode)
        card1 = ModernCard(
            panel, 
            title="User Profile", 
            bg_color="#FFFFFF", 
            border_color="#D1D5DB", 
            title_color="#1F2937",
            line_color="#E5E7EB",
            corner_radius=14
        )
        
        # Menambahkan isi widget ke Card 1
        card1.AddContent(wx.StaticText(card1, label="Name: John Doe"))
        card1.AddContent(wx.StaticText(card1, label="Role: Software Engineer"), border=5, flag=wx.TOP)
        card1.AddContent(wx.Button(card1, label="Edit Profile"), border=15, flag=wx.TOP | wx.EXPAND)

        # Card 2: Tema Gelap / Modern Dark Accent
        custom_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        card2 = ModernCard(
            panel, 
            title="System Analytics", 
            bg_color="#1E1E2E", 
            border_color="#313244", 
            title_color="#CDD6F4", 
            line_color="#45475A",
            corner_radius=16,
            title_font=custom_font
        )
        
        # Menambahkan isi widget ke Card 2
        lbl = wx.StaticText(card2, label="Server Status: Operational")
        lbl.SetForegroundColour("#A6E3A1")
        card2.AddContent(lbl)
        
        gauge = wx.Gauge(card2, range=100)
        gauge.SetValue(75)
        card2.AddContent(gauge, border=10, flag=wx.TOP | wx.EXPAND)
        
        card2.AddContent(wx.CheckBox(card2, label="Enable Realtime Monitoring"), border=15, flag=wx.TOP)

        # Layout Sizer Frame
        main_sizer.Add(card1, 1, wx.EXPAND | wx.ALL, 20)
        main_sizer.Add(card2, 1, wx.EXPAND | wx.ALL, 20)
        
        panel.SetSizer(main_sizer)
        self.Center()

if __name__ == "__main__":
    app = wx.App()
    frame = DemoFrame()
    frame.Show()
    app.MainLoop()