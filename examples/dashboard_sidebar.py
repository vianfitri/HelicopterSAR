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

        # Load image helicopter
        self.heli_image = wx.Image("examples/images/bell412pps.png")
        self.img_heli_orig = wx.Image("examples/images/bell412pps.png")

        # Load base track image
        self.base_image = wx.Image("examples/images/base_track.png")
        self.img_base_orig = wx.Image("examples/images/base_track.png")

        # Load base trolley image
        self.base_trolley_image = wx.Image("examples/images/base_trolley.png")
        self.img_trolley_orig = wx.Image("examples/images/base_trolley.png")

        # Load base fence image
        self.base_fence_image = wx.Image("examples/images/base_fence.png")
        self.img_fence_orig = wx.Image("examples/images/base_fence.png")

        # Reference Constants
        self.ref_pixel = 1322
        self.ref_meter = 12

        # Cache Bitmap & Off-screen Background Buffer
        self.bg_buffer = None
        self.fg_buffer = None
        self.base_bitmap = None
        self.fence_bitmap = None
        self.heli_bitmap = None
        self.trolley_bitmap = None

        # State Trackbar Control (0 = Kanan, 100 = Kiri)
        self.trackbar_value = 0 # Default di kanan
        self.is_dragging_trackbar = False

        # Default position
        self.heli_x, self.heli_y = 0, 0
        self.trolley_x, self.trolley_y = 0, 0
        self.base_x, self.base_y = 0, 0
        self.fence_x, self.fence_y = 0, 0

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)

        # Mouse Events untuk Interaksi Trackbar
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)

    def calculate_positions_from_trackbar(self, scale):
        """Menghitung posisi X Helicopter & Trolley berdasarkan nilai Trackbar (0..100)."""
        # Rentang pergerakan horizontal (Offset X)
        # 0 = Kanan (posisi dasar), 100 = Kiri (bergeser sejauh jarak lintasan)
        max_offset_x = int(round(710 * scale))
        
        # Invert logika: 0 di kanan (offset = 0), 100 di kiri (offset = max_offset_x)
        current_offset = int(round((self.trackbar_value / 100.0) * max_offset_x))

        # Posisi dasar (Kanan)
        base_trolley_x = self.base_x + int(round(1102 * scale))
        base_heli_x = int(round(910 * scale))

        # Geser ke kiri berdasarkan trackbar
        self.trolley_x = base_trolley_x - current_offset
        self.heli_x = base_heli_x - current_offset

    def update_background_buffer(self, canvas_w, canvas_h, scale):
        # render fence and base once at resize
        if canvas_w <= 0 or canvas_h <= 0:
            return

        self.bg_buffer = wx.Bitmap(canvas_w, canvas_h)
        mem_dc_bg = wx.MemoryDC(self.bg_buffer)
        gc_bg = wx.GraphicsContext.Create(mem_dc_bg)

        if gc_bg:
            # Render Background Color
            gc_bg.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
            gc_bg.DrawRectangle(0, 0, canvas_w, canvas_h)

            # Render Fence (Statis Belakang)
            gc_bg.DrawBitmap(
                self.fence_bitmap,
                self.fence_x, self.fence_y,
                self.fence_bitmap.GetWidth(), self.fence_bitmap.GetHeight()
            )

        #mem_dc_bg.SelectObject(wx.NullBitmap)

        #self.fg_buffer = wx.Bitmap(canvas_w, canvas_h)
        #mem_dc_fg = wx.MemoryDC(self.fg_buffer)
        #gc_fg = wx.GraphicsContext.Create(mem_dc_fg)

        #if gc_fg:
            # Render Base Track (Statis Depan)
            gc_bg.DrawBitmap(
                self.base_bitmap,
                self.base_x, self.base_y,
                self.base_bitmap.GetWidth(), self.base_bitmap.GetHeight()
            )

            # Draw Border Base Track jika diperlukan
            #gc_fg.SetPen(wx.Pen(wx.Colour(255, 128, 0), 2))
            #gc_fg.SetBrush(wx.TRANSPARENT_BRUSH)
            #gc_fg.DrawRectangle(self.base_x, self.base_y, self.base_bitmap.GetWidth(), self.base_bitmap.GetHeight())

        mem_dc_bg.SelectObject(wx.NullBitmap)

    def on_resize(self, event):
        canvas_w, canvas_h = self.GetClientSize()

        if canvas_w > 0 and canvas_h > 0:
            self.scale = canvas_w / 2500.0

            # Skala gambar secara hemat memori (Scale hanya saat resize)
            img_base = self.img_base_orig.Scale(
                max(1, int(round(self.img_base_orig.GetWidth() * self.scale))),
                max(1, int(round(self.img_base_orig.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.base_bitmap = wx.Bitmap(img_base)

            img_fence = self.img_fence_orig.Scale(
                max(1, int(round(self.img_fence_orig.GetWidth() * self.scale))),
                max(1, int(round(self.img_fence_orig.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.fence_bitmap = wx.Bitmap(img_fence)

            img_trolley = self.img_trolley_orig.Scale(
                max(1, int(round(self.img_trolley_orig.GetWidth() * self.scale))),
                max(1, int(round(self.img_trolley_orig.GetHeight() * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.trolley_bitmap = wx.Bitmap(img_trolley)

            # Perhitungan khusus helikopter
            heli_pixel, heli_meter = 510, 5.05
            ref_scale = self.ref_pixel / self.ref_meter
            heli_w_meter = 1408 * heli_meter / heli_pixel
            heli_h_meter = 768 * heli_meter / heli_pixel
            new_heli_w = heli_w_meter * ref_scale
            new_heli_h = heli_h_meter * ref_scale

            img_heli = self.img_heli_orig.Scale(
                max(1, int(round(new_heli_w * self.scale))),
                max(1, int(round(new_heli_h * self.scale))),
                wx.IMAGE_QUALITY_HIGH
            )
            self.heli_bitmap = wx.Bitmap(img_heli)

            # Hitung Posisi Koordinat
            self.base_x = int(round(110 * self.scale))
            self.base_y = int(round(309 * self.scale))
            self.fence_x = self.base_x + int(round(1182 * self.scale))
            self.fence_y = self.base_y + int(round(272 * self.scale))
            self.trolley_x = self.base_x + int(round(1102 * self.scale))
            self.trolley_y = self.base_y + int(round(319 * self.scale))
            self.heli_x = int(round(910 * self.scale))
            self.heli_y = 0

            # Hitung geometri Trackbar sesuai skala
            self.trackbar_x = self.base_x + int(round(592 * self.scale))
            self.trackbar_y = self.base_y + self.base_bitmap.GetHeight() + int(round(15 * self.scale)) # Di bawah base_track
            self.trackbar_length = int(round(710 * self.scale))

            # Hitung posisi X dinamis berdasarkan nilai trackbar
            self.calculate_positions_from_trackbar(self.scale)

            # Update Background Buffer Statis
            self.update_background_buffer(canvas_w, canvas_h, self.scale)

        self.Refresh(False)
        event.Skip()

    # =======================================================
    # INTERAKSI MOUSE UNTUK TRACKBAR
    # =======================================================
    def get_thumb_rect(self):
        """Mendapatkan bounding box dari tombol/thumb trackbar untuk deteksi klik."""
        # 0 = Kanan, 100 = Kiri
        ratio = (100 - self.trackbar_value) / 100.0
        thumb_center_x = self.trackbar_x + int(round(ratio * self.trackbar_length))
        
        radius = int(round(10 * getattr(self, 'scale', 1.0)))
        return wx.Rect(thumb_center_x - radius, self.trackbar_y - radius, radius * 2, radius * 2)

    def update_value_from_mouse(self, mouse_x):
        """Memperbarui nilai trackbar (0-100) berdasarkan koordinat mouse."""
        rel_x = mouse_x - self.trackbar_x
        rel_x = max(0, min(self.trackbar_length, rel_x)) # Clamp nilai
        
        # 0 di kanan, 100 di kiri
        ratio = rel_x / float(self.trackbar_length) if self.trackbar_length > 0 else 0
        self.trackbar_value = int(round((1.0 - ratio) * 100))
        
        # Perbarui posisi gambar dinamis
        self.calculate_positions_from_trackbar(self.scale)
        self.Refresh(False)

    def on_mouse_down(self, event):
        pos = event.GetPosition()
        thumb_rect = self.get_thumb_rect()
        
        # Perbesar hit-area sedikit agar mudah di-klik
        thumb_rect.Inflate(5, 5)
        
        if thumb_rect.Contains(pos):
            self.is_dragging_trackbar = True
            self.CaptureMouse()
        elif self.trackbar_x <= pos.x <= (self.trackbar_x + self.trackbar_length) and \
             abs(pos.y - self.trackbar_y) <= 15:
            # Klik langsung pada garis trackbar
            self.is_dragging_trackbar = True
            if self.HasCapture():
                self.ReleaseMouse()
            self.CaptureMouse()
            self.update_value_from_mouse(pos.x)

    def on_mouse_move(self, event):
        if self.is_dragging_trackbar and event.Dragging():
            self.update_value_from_mouse(event.GetPosition().x)

    def on_mouse_up(self, event):
        if self.is_dragging_trackbar:
            self.is_dragging_trackbar = False
            if self.HasCapture():
                self.ReleaseMouse()

    def update_positions(self, heli_pos=None, trolley_pos=None):
        if heli_pos:
            self.heli_x, self.heli_y = heli_pos
        if trolley_pos:
            self.trolley_x, self.trolley_y = trolley_pos
            
        self.Refresh(False)

    def on_size(self, event):
        # Canvas size 
        canvas_w, canvas_h = self.GetClientSize()

        image_base = self.base_image
        image_trolley = self.base_trolley_image
        image_fence = self.base_fence_image
        image_heli = self.heli_image

        print(f"canvas w: {canvas_w}, canvas h: {canvas_h}")

        # image resize
        if canvas_w > 0 and canvas_h > 0:
            scale = canvas_w / 2500 # minimum lebar gambar dengan referensi base

            print(f"scale: {scale}")
            print(f"base w: {image_base.GetWidth()}, base h: {image_base.GetHeight()}")

            # ======================================
            # base image scaling
            image_base = image_base.Scale(
                int(round(image_base.GetWidth() * scale)),
                int(round(image_base.GetHeight() * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create base bitmap
            self.base_bitmap = wx.Bitmap(image_base)

            # set position of base bitmap image
            self.base_x = int(round(110 * scale)) # pos x jika lebar gambar max 2500
            self.base_y = int(round(309 * scale))

            # ======================================
            # trolley image scaling
            image_trolley = image_trolley.Scale(
                int(round(image_trolley.GetWidth() * scale)),
                int(round(image_trolley.GetHeight() * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create trolley bitmap
            self.trolley_bitmap = wx.Bitmap(image_trolley)

            # set position of trolley bitmap image
            self.trolley_x = self.base_x + int(round(1102 * scale))
            self.trolley_y = self.base_y + int(round(319 * scale))

            # ======================================
            # fence image scaling
            image_fence = image_fence.Scale(
                int(round(image_fence.GetWidth() * scale)),
                int(round(image_fence.GetHeight() * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create fence bitmap
            self.fence_bitmap = wx.Bitmap(image_fence)

            # set position of fence bitmap image
            self.fence_x = self.base_x + int(round(1182 * scale))
            self.fence_y = self.base_y + int(round(272 * scale))

            # ======================================
            # helicopter image scaling
            heli_pixel = 510
            heli_meter = 5.05

            ref_scale = self.ref_pixel / self.ref_meter
            heli_image_meter_width = 1408 * heli_meter / heli_pixel
            heli_image_meter_height = 768 * heli_meter / heli_pixel
            new_heli_width = heli_image_meter_width * ref_scale
            new_heli_height = heli_image_meter_height * ref_scale

            image_heli = image_heli.Scale(
                int(round(new_heli_width * scale)),
                int(round(new_heli_height * scale)),
                wx.IMAGE_QUALITY_HIGH
            )

            # create heli bitmap
            self.heli_bitmap = wx.Bitmap(image_heli)

            # set position of heli bitmap image
            self.heli_x = int(round(910 * scale))
            self.heli_y = 0
            
        self.Refresh()
        event.Skip()

    # =======================================================
    # RENDERING
    # =======================================================
    def draw_trackbar(self, gc):
        """Menggambar visual trackbar secara kustom menggunakan GraphicsContext."""
        # 1. Garis Lintasan Trackbar (Track Rail)
        gc.SetPen(wx.Pen(wx.Colour(120, 140, 160), 4))
        gc.StrokeLine(self.trackbar_x, self.trackbar_y, self.trackbar_x + self.trackbar_length, self.trackbar_y)

        # 2. Tanda Batas Kiri & Kanan (Ticks)
        gc.SetPen(wx.Pen(wx.Colour(80, 90, 100), 2))
        tick_h = int(round(8 * self.scale))
        gc.StrokeLine(self.trackbar_x, self.trackbar_y - tick_h, self.trackbar_x, self.trackbar_y + tick_h) # 100 (Kiri)
        gc.StrokeLine(self.trackbar_x + self.trackbar_length, self.trackbar_y - tick_h, 
                      self.trackbar_x + self.trackbar_length, self.trackbar_y + tick_h) # 0 (Kanan)

        # 3. Tombol Geser (Thumb Handle)
        # Ratio: 0 = Kanan, 100 = Kiri
        ratio = (100 - self.trackbar_value) / 100.0
        thumb_x = self.trackbar_x + int(round(ratio * self.trackbar_length))
        radius = int(round(10 * self.scale))

        # Warna Tombol (Orange saat di-drag)
        fill_color = wx.Colour(255, 128, 0) if self.is_dragging_trackbar else wx.Colour(0, 120, 215)
        gc.SetBrush(wx.Brush(fill_color))
        gc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 2))
        gc.DrawEllipse(thumb_x - radius, self.trackbar_y - radius, radius * 2, radius * 2)

        # 4. Teks Nilai Trackbar (Indikator 0..100)
        font = wx.Font(int(round(9 * self.scale)), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, wx.Colour(50, 50, 50))
        gc.DrawText("100", self.trackbar_x - int(round(25 * self.scale)), self.trackbar_y - int(round(8 * self.scale)))
        gc.DrawText("0", self.trackbar_x + self.trackbar_length + int(round(10 * self.scale)), self.trackbar_y - int(round(8 * self.scale)))

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        if not gc or not self.bg_buffer or not self.bg_buffer.IsOk():
            return

        # draw blit background cache
        gc.DrawBitmap(self.bg_buffer, 0, 0, self.bg_buffer.GetWidth(), self.bg_buffer.GetHeight())

        # draw helicopter image
        gc.DrawBitmap(
            self.heli_bitmap,
            self.heli_x, self.heli_y,
            self.heli_bitmap.GetWidth(), self.heli_bitmap.GetHeight()
        )

        # draw trolley
        gc.DrawBitmap(
            self.trolley_bitmap,
            self.trolley_x, self.trolley_y,
            self.trolley_bitmap.GetWidth(), self.trolley_bitmap.GetHeight()
        )

        # Border Helikopter
        #gc.SetPen(wx.Pen(wx.Colour(255, 128, 0), 2))
        #gc.SetBrush(wx.TRANSPARENT_BRUSH)
        #gc.DrawRectangle(self.heli_x, self.heli_y, self.heli_bitmap.GetWidth(), self.heli_bitmap.GetHeight())

        # draw blit foreground cache
        #gc.DrawBitmap(self.fg_buffer, 0, 0, self.fg_buffer.GetWidth(), self.fg_buffer.GetHeight())

        self.draw_trackbar(gc)

        #width, height = self.GetClientSize()

        # Background
        #gc.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
        #gc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))
        #gc.DrawRectangle(0, 0, width, height)

        # Draw fence
        #gc.DrawBitmap(
        #    self.fence_bitmap,
        #    self.fence_x,
        #    self.fence_y,
        #    self.fence_bitmap.GetWidth(),
        #    self.fence_bitmap.GetHeight()
        #)

        # Draw helicopter
        #gc.DrawBitmap(
        #    self.heli_bitmap,
        #    self.heli_x,
        #    self.heli_y,
        #    self.heli_bitmap.GetWidth(),
        #    self.heli_bitmap.GetHeight()
        #)

        # Draw Trolley
        #gc.DrawBitmap(
        #    self.trolley_bitmap,
        #    self.trolley_x,
        #    self.trolley_y,
        #    self.trolley_bitmap.GetWidth(),
        #    self.trolley_bitmap.GetHeight()
        #)

        # Draw base
        #gc.DrawBitmap(
        #    self.base_bitmap,
        #    self.base_x,
        #    self.base_y,
        #    self.base_bitmap.GetWidth(),
        #    self.base_bitmap.GetHeight()
        #)

        # draw border bitmap
        #gc.SetPen(wx.Pen(wx.Colour(255, 128, 0), 2))
        #gc.SetBrush(wx.TRANSPARENT_BRUSH)

        #gc.DrawRectangle(self.heli_x, self.heli_y, self.heli_bitmap.GetWidth(), self.heli_bitmap.GetHeight())
        #gc.DrawRectangle(self.base_x, self.base_y, self.base_bitmap.GetWidth(), self.base_bitmap.GetHeight())

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

        #print(f"pos x: {self.pos_x}, pos y: {self.pos_y}, clientSizeHeight: {self.clientSizeHeight}, bitmapheight: {self.BitmapHeight}")

        self.Refresh()
        event.Skip()

    def on_paint(self, event):

        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        width, height = self.GetClientSize()

        # Background
        #gc.SetBrush(wx.Brush(wx.Colour(235, 240, 245)))
        gc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))
        gc.DrawRectangle(0, 0, width, height)

        # Gambar helicopter
        gc.DrawBitmap(
            self.bitmap,
            self.pos_x,
            self.pos_y,
            self.bitmap.GetWidth(),
            self.bitmap.GetHeight()
        )

        # Gambar Wire
        #gc.SetPen(wx.Pen(wx.Colour(0, 0, 0)))
        #gc.DrawLines()

        # draw border bitmap
        #gc.SetPen(wx.Pen(wx.Colour(255, 128, 0), 2))
        #gc.SetBrush(wx.TRANSPARENT_BRUSH)

        #gc.DrawRectangle(self.pos_x, self.pos_y, self.bitmap.GetWidth(), self.bitmap.GetHeight())

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