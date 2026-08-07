import wx


# ==========================
# Color Theme
# ==========================
BG_COLOR = "#F5F6F8"
TITLE_COLOR = "#2F343A"
SIDEBAR_COLOR = "#383E45"
ACCENT = "#FF7A00"

TEXT_LIGHT = "#FFFFFF"
TEXT_DARK = "#222222"


# ==========================
# Rounded Button
# ==========================
class SidebarButton(wx.Control):

    def __init__(self, parent, label):
        super().__init__(parent, size=(180, 50))

        self.label = label
        self.hover = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)

    def on_enter(self, event):
        self.hover = True
        self.Refresh()

    def on_leave(self, event):
        self.hover = False
        self.Refresh()

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        w, h = self.GetSize()

        dc.SetBackground(wx.Brush(SIDEBAR_COLOR))
        dc.Clear()

        radius = 12

        if self.hover:
            color = wx.Colour(255, 122, 0)
        else:
            color = wx.Colour(70, 75, 82)

        gc.SetBrush(wx.Brush(color))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, 0, w, h, radius)

        gc.SetFont(
            wx.Font(10, wx.FONTFAMILY_DEFAULT,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_BOLD),
            TEXT_LIGHT)

        tw, th = gc.GetTextExtent(self.label)

        gc.DrawText(
            self.label,
            (w - tw) / 2,
            (h - th) / 2
        )

# ==========================
# Canvas Helicopter
# ==========================
class CanvasHelicopter(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Load gambar
        self.imageScale = 0.2
        image = wx.Image("examples/images/bell412pps.png")
        imageWidth = int(round(image.GetWidth() * self.imageScale))
        imageHeight = int(round(image.GetHeight() * self.imageScale))
        image = image.Scale(
            imageWidth,
            imageHeight,
            wx.IMAGE_QUALITY_HIGH
        )
        self.bitmap = wx.Bitmap(image)

        # Posisi gambar
        self.pos_x = 100
        self.pos_y = 100

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        # Gambar selalu berada di tengah secara vertikal
        self.clientSizeHeight = self.GetClientSize().height
        self.clientSizeWidth = self.GetClientSize().width
        self.BitmapHeight = self.bitmap.GetHeight()
        #self.pos_y = (
        #    self.clientSizeHeight - self.BitmapHeight
        #) // 2

        self.pos_x = self.clientSizeWidth - 10 - self.bitmap.GetWidth()
        self.pos_y = 10

        #print(f"pos y: {self.pos_y}, clientSizeHeight: {self.clientSizeHeight}, bitmapheight: {self.BitmapHeight}")
        

        self.Refresh()
        event.Skip()

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        width, height = self.GetClientSize()

        # Background
        gc.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
        #gc.SetBrush(wx.Brush(self.Parent.GetBackgroundColour()))
        gc.DrawRectangle(0, 0, width, height)

        # Garis lintasan
        gc.SetPen(wx.Pen(wx.Colour(180, 180, 180), 2))
        gc.StrokeLine(
            20,
            height // 2,
            width - 20,
            height // 2
        )

        # Gambar helicopter
        gc.DrawBitmap(
            self.bitmap,
            self.pos_x,
            self.pos_y,
            self.bitmap.GetWidth(),
            self.bitmap.GetHeight()
        )

        # draw border bitmap
        gc.SetPen(wx.Pen(wx.Colour(255, 128, 0), 2))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)

        gc.DrawRectangle(self.pos_x, self.pos_y, self.bitmap.GetWidth(), self.bitmap.GetHeight())

# ==========================
# Canvas Hoist
# ==========================
class CanvasHoist(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Load gambar
        self.imageScale = 0.15
        image = wx.Image("examples/images/bell412pps.png")
        imageWidth = int(round(image.GetWidth() * self.imageScale))
        imageHeight = int(round(image.GetHeight() * self.imageScale))
        image = image.Scale(
            imageWidth,
            imageHeight,
            wx.IMAGE_QUALITY_HIGH
        )
        self.bitmap = wx.Bitmap(image)

        # Posisi gambar
        self.pos_x = 100
        self.pos_y = 100

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        # Gambar selalu berada di tengah secara vertikal
        self.clientSizeHeight = self.GetClientSize().height
        self.clientSizeWidth = self.GetClientSize().width
        self.BitmapHeight = self.bitmap.GetHeight()
        #self.pos_y = (
        #    self.clientSizeHeight - self.BitmapHeight
        #) // 2

        self.pos_x = (self.clientSizeWidth - self.bitmap.GetWidth()) / 2
        self.pos_y = 10

        print(f"pos x: {self.pos_x}, pos y: {self.pos_y}, clientSizeHeight: {self.clientSizeHeight}, bitmapheight: {self.BitmapHeight}")

        self.Refresh()
        event.Skip()

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        width, height = self.GetClientSize()

        # Background
        gc.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
        #gc.SetBrush(wx.Brush(self.Parent.GetBackgroundColour()))
        gc.DrawRectangle(0, 0, width, height)

        # Gambar helicopter
        gc.DrawBitmap(
            self.bitmap,
            self.pos_x,
            self.pos_y,
            self.bitmap.GetWidth(),
            self.bitmap.GetHeight()
        )

        # draw border bitmap
        gc.SetPen(wx.Pen(wx.Colour(255, 128, 0), 2))
        gc.SetBrush(wx.TRANSPARENT_BRUSH)

        gc.DrawRectangle(self.pos_x, self.pos_y, self.bitmap.GetWidth(), self.bitmap.GetHeight())

# ==========================
# Modern Card
# ==========================
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
        super().__init__(parent, id, pos=pos, size=size, style=style | wx.TRANSPARENT_WINDOW | wx.BORDER_NONE)

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

        # Shadow offset configuration
        shadow_offset_x = 1
        shadow_offset_y = 0
        shadow_blur = 1.01

        # 1. Gambar Soft Drop Shadow di sekeliling card
        shadow_path = gc.CreatePath()
        #shadow_path.AddRoundedRectangle(card_x + shadow_offset_x, card_y + shadow_offset_y, card_w * shadow_blur, card_h * shadow_blur, self._corner_radius)
        shadow_path.AddRoundedRectangle(card_x + 1, card_y + 1, card_w + 4, card_h + 4, self._corner_radius)
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 8)))) # Black transparan
        #gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(wx.Colour("#FF0000")).Width(1)))
        gc.SetPen(wx.NullPen)
        gc.FillPath(shadow_path)
        #gc.DrawPath(shadow_path)

        # 2. Gambar Background Utama Card
        card_path = gc.CreatePath()
        card_path.AddRoundedRectangle(card_x, card_y, card_w, card_h, self._corner_radius)
        gc.SetBrush(gc.CreateBrush(wx.Brush(self._bg_color)))
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self._border_color).Width(1)))
        gc.DrawPath(card_path)

        #print(f"width: {width}, height: {height}, card_x: {card_x}, card_y: {card_y}, card_w: {card_w}, card_h: {card_h}")

        # 3. Gambar Text Title
        gc.SetFont(self._title_font, self._title_color)
        text_x = card_x + self._padding
        text_y = card_y + (self._title_height // 2) - 8
        gc.DrawText(self._title, text_x, text_y)

        # 4. Gambar Border Pembatas + Soft Line Shadow di Bawah Title
        line_y = card_y + self._title_height
        
        # Soft Shadow Line (Bayangan halus di bawah garis)
        line_shadow_path = gc.CreatePath()
        line_shadow_path.MoveToPoint(card_x + 6, line_y + 1)
        line_shadow_path.AddLineToPoint(card_x + card_w - 6, line_y + 1)
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(wx.Colour(0, 0, 0, 10)).Width(2)))
        gc.StrokePath(line_shadow_path)

        # Garis Pembatas Utama (Subtle Border)
        line_path = gc.CreatePath()
        line_path.MoveToPoint(card_x + 6, line_y)
        line_path.AddLineToPoint(card_x + card_w - 6, line_y)
        gc.SetPen(gc.CreatePen(wx.GraphicsPenInfo(self._line_color).Width(1)))
        gc.StrokePath(line_path)

# ==========================
# Main Frame
# ==========================
class Dashboard(wx.Frame):

    def __init__(self):
        super().__init__(
            None,
            title="SAR Dashboard",
            size=(1300, 750)
        )

        self.SetBackgroundColour(BG_COLOR)

        panel = wx.Panel(self)
        panel.SetBackgroundColour(BG_COLOR)

        root = wx.BoxSizer(wx.VERTICAL)

        # =====================================================
        # TITLE BAR
        # =====================================================

        titleBar = wx.Panel(panel, size=(-1, 70))
        titleBar.SetBackgroundColour(TITLE_COLOR)

        titleSizer = wx.BoxSizer(wx.HORIZONTAL)

        title = wx.StaticText(titleBar, label="Helicopter Rescue Simulator")
        title.SetForegroundColour(TEXT_LIGHT)

        title.SetFont(
            wx.Font(
                16,
                wx.FONTFAMILY_SWISS,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD
            )
        )

        accent = wx.Panel(titleBar, size=(8, 40))
        accent.SetBackgroundColour(ACCENT)

        titleSizer.AddSpacer(20)
        titleSizer.Add(accent, 0, wx.ALIGN_CENTER_VERTICAL)
        titleSizer.AddSpacer(15)
        titleSizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL)
        titleSizer.AddStretchSpacer()

        titleBar.SetSizer(titleSizer)

        root.Add(titleBar, 0, wx.EXPAND)

        # =====================================================
        # BODY
        # =====================================================

        body = wx.BoxSizer(wx.HORIZONTAL)

        # ---------------- Sidebar ------------------

        sidebar = wx.Panel(panel, size=(220, -1))
        sidebar.SetBackgroundColour(SIDEBAR_COLOR)

        sideSizer = wx.BoxSizer(wx.VERTICAL)

        sideSizer.AddSpacer(30)

        btn1 = SidebarButton(sidebar, "Monitoring")
        btn2 = SidebarButton(sidebar, "Settings")

        sideSizer.Add(btn1, 0,
                      wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 15)

        sideSizer.Add(btn2, 0,
                      wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 15)

        sideSizer.AddStretchSpacer()

        sidebar.SetSizer(sideSizer)

        # ---------------- Content ------------------

        content = wx.Panel(panel)
        content.SetBackgroundColour(BG_COLOR)

        contentSizer = wx.BoxSizer(wx.HORIZONTAL)

        card1 = ModernCard(
            content, 
            title="Helicopter Position", 
            bg_color="#FFFFFF", 
            border_color="#D1D5DB", 
            title_color="#1F2937",
            line_color="#E5E7EB",
            corner_radius=14
        )

        self.helicopterCanvas = CanvasHelicopter(card1)

        card1.AddContent(self.helicopterCanvas, 1, flag=wx.EXPAND)

        card2 = ModernCard(
            content, 
            title="Hoist Length", 
            bg_color="#FFFFFF", 
            border_color="#D1D5DB", 
            title_color="#1F2937",
            line_color="#E5E7EB",
            corner_radius=14
        )

        self.hoistCanvas = CanvasHoist(card2)

        card2.AddContent(self.hoistCanvas, 1, flag=wx.EXPAND)

        contentSizer.Add(card1, proportion=7, flag=wx.EXPAND)
        contentSizer.Add(card2, proportion=3, flag=wx.EXPAND)

        content.SetSizer(contentSizer)

        body.Add(sidebar, 0, wx.EXPAND)
        body.Add(content, 1, wx.EXPAND | wx.ALL, 15)

        root.Add(body, 1, wx.EXPAND)

        panel.SetSizer(root)

    def on_slider_helicopter(self, event):
            self.helicopterCanvas.pos_x = self.slider.GetValue()
            self.helicopterCanvas.Refresh() 


# ==========================
# Main
# ==========================
if __name__ == "__main__":
    app = wx.App()
    frame = Dashboard()
    frame.Center()
    frame.Show()
    app.MainLoop()