import wx


class CardPanel(wx.Panel):

  def __init__(
      self,
      parent,
      title="Card Title",
      font=None,
      bg_color=wx.Colour(255, 255, 255),
      title_bg_color=wx.Colour(245, 245, 245),
      text_color=wx.Colour(30, 30, 30),
      size=wx.DefaultSize,
      corner_radius=12,
      transparent=False,
  ):
    super().__init__(parent, size=size)

    # Simpan parameter konfigurasi
    self.card_title = title
    self.card_font = (
        font
        if font
        else wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
    )
    self.bg_color = bg_color
    self.title_bg_color = title_bg_color
    self.text_color = text_color
    self.corner_radius = corner_radius
    self.is_transparent = transparent

    if self.is_transparent:
      self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
    else:
      self.SetBackgroundColour(parent.GetBackgroundColour())

    # Layout Utama Card
    self.main_sizer = wx.BoxSizer(wx.VERTICAL)

    # 1. Title Bar
    self.title_panel = wx.Panel(self)
    if not self.is_transparent:
      self.title_panel.SetBackgroundColour(self.title_bg_color)

    title_sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.title_label = wx.StaticText(
        self.title_panel, label=self.card_title
    )
    self.title_label.SetFont(self.card_font)
    self.title_label.SetForegroundColour(self.text_color)
    title_sizer.Add(
        self.title_label,
        flag=wx.ALIGN_CENTER_VERTICAL
        | wx.LEFT
        | wx.RIGHT
        | wx.TOP
        | wx.BOTTOM,
        border=10,
    )
    self.title_panel.SetSizer(title_sizer)

    self.main_sizer.Add(self.title_panel, flag=wx.EXPAND)

    # 2. Shadow Line (Pemisah Title dan Konten)
    self.shadow_line = wx.Panel(self, size=(-1, 2))
    self.shadow_line.SetBackgroundColour(wx.Colour(220, 220, 220))
    self.main_sizer.Add(self.shadow_line, flag=wx.EXPAND)

    # 3. Konten Panel (Tempat menambahkan widget anak nantinya)
    self.content_panel = wx.Panel(self)
    if not self.is_transparent:
      self.content_panel.SetBackgroundColour(self.bg_color)
    self.content_sizer = wx.BoxSizer(wx.VERTICAL)
    self.content_panel.SetSizer(self.content_sizer)

    self.main_sizer.Add(self.content_panel, 1, flag=wx.EXPAND)
    self.SetSizer(self.main_sizer)

    # Event Binding untuk mengatasi sisa gambar saat resize & menggambar rounded corner
    self.Bind(wx.EVT_PAINT, self.on_paint)
    self.Bind(wx.EVT_SIZE, self.on_size)

  def GetContentPanel(self):
    """Mengembalikan panel konten agar user bisa menambahkan widget di dalamnya."""
    return self.content_panel

  def GetContentSizer(self):
    """Mengembalikan sizer konten."""
    return self.content_sizer

  def on_size(self, event):
    """Memaksa panel untuk membersihkan sisa render saat ukuran diubah (resize)."""
    self.Refresh()
    event.Skip()

  def on_paint(self, event):
    """Menggambar sudut melengkung (rounded corner) dan background."""
    dc = wx.PaintDC(self)
    gc = wx.GraphicsContext.Create(dc)

    if not gc:
      return

    rect = self.GetClientRect()

    # Buat path rounded rectangle
    path = gc.CreatePath()
    # Mengurangi sedikit ukuran width/height agar garis tepi tidak terpotong
    path.AddRoundedRectangle(
        rect.x, rect.y, rect.width - 1, rect.height - 1, self.corner_radius
    )

    if self.is_transparent:
      # Jika transparan, potong area luar card agar latar belakang parent terlihat
      gc.Clip(path)
      # Bersihkan background dengan warna parent
      dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
      dc.Clear()
    else:
      # Jika tidak transparan, isi dengan warna background card
      gc.SetBrush(wx.Brush(self.bg_color))
      gc.SetPen(wx.Pen(wx.Colour(200, 200, 200), 1))
      gc.DrawPath(path)


# ==========================================
# CONTOH PENGGUNAAN (Main Frame)
# ==========================================
class MainFrame(wx.Frame):

  def __init__(self):
    super().__init__(
        None, title="Reusable Card Panel Demo", size=(600, 450)
    )

    panel = wx.Panel(self)
    panel.SetBackgroundColour(wx.Colour(240, 242, 245))  # Background parent

    main_sizer = wx.BoxSizer(wx.HORIZONTAL)

    # Contoh 1: Card Panel Biasa (Solid dengan Corner Radius)
    card1 = CardPanel(
        panel,
        title="Informasi Profil",
        bg_color=wx.Colour(255, 255, 255),
        title_bg_color=wx.Colour(235, 240, 255),
        corner_radius=16,
        size=(260, -1),
    )
    # Menambahkan konten ke dalam card 1
    c_sizer1 = card1.GetContentSizer()
    lbl1 = wx.StaticText(
        card1.GetContentPanel(), label="Nama: John Doe\nPekerjaan: Developer"
    )
    c_sizer1.Add(lbl1, flag=wx.ALL, border=15)

    # Contoh 2: Card Panel dengan mode Transparan
    card2 = CardPanel(
        panel,
        title="Statistik Sistem",
        corner_radius=16,
        transparent=True,  # Mengaktifkan mode transparan
        size=(260, -1),
    )
    # Menambahkan konten ke dalam card 2
    c_sizer2 = card2.GetContentSizer()
    btn = wx.Button(card2.GetContentPanel(), label="Refresh Data")
    c_sizer2.Add(btn, flag=wx.ALL | wx.EXPAND, border=15)

    # Masukkan card ke layout utama frame dengan proporsional (mengikuti resize parent)
    main_sizer.Add(card1, 1, flag=wx.EXPAND | wx.ALL, border=15)
    main_sizer.Add(card2, 1, flag=wx.EXPAND | wx.ALL, border=15)

    panel.SetSizer(main_sizer)
    self.Center()


if __name__ == "__main__":
  app = wx.App()
  frame = MainFrame()
  frame.Show()
  app.MainLoop()