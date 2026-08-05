import wx

class CustomButton(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition, 
                 size=(140, 40), style=wx.BORDER_NONE):
        super().__init__(parent, id, pos, size, style)
        
        self.label = label
        self.is_hover = False
        self.is_pressed = False
        
        # Skema Warna
        self.bg_normal = wx.Colour(41, 128, 185)   # Biru
        self.bg_hover = wx.Colour(52, 152, 219)    # Biru Cerah
        self.bg_pressed = wx.Colour(21, 67, 96)    # Biru Gelap
        self.text_color = wx.Colour(255, 255, 255) # Putih
        self.radius = 10                            # Lengkungan sudut (Rounded)

        # Event Binding untuk Render & Interaksi Mouse
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None) # Mencegah flickering

    def DoGetBestSize(self):
        """Menentukan ukuran default/terbaik untuk sizer."""
        return wx.Size(140, 40)

    # --- Mouse Event Handlers ---
    def _on_enter(self, event):
        self.is_hover = True
        self.Refresh()

    def _on_leave(self, event):
        self.is_hover = False
        self.is_pressed = False
        self.Refresh()

    def _on_left_down(self, event):
        self.is_pressed = True
        self.Refresh()

    def _on_left_up(self, event):
        if self.is_pressed:
            self.is_pressed = False
            self.Refresh()
            # Memicu event klik wx.EVT_BUTTON standar
            evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            evt.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(evt)

    # --- Drawing Logic ---
    def _on_paint(self, event):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        width, height = self.GetClientSize()

        # 1. Tentukan warna background berdasarkan state
        if self.is_pressed:
            bg_color = self.bg_pressed
        elif self.is_hover:
            bg_color = self.bg_hover
        else:
            bg_color = self.bg_normal

        # 2. Gambar Background Rounded Rectangle
        gc.SetBrush(gc.CreateBrush(wx.Brush(bg_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(bg_color)))
        gc.DrawRoundedRectangle(0, 0, width, height, self.radius)

        # 3. Gambar Teks di Tengah (Center)
        font = self.GetFont()
        if not font.IsOk():
            font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, self.text_color)

        text_w, text_h = gc.GetTextExtent(self.label)
        text_x = (width - text_w) / 2
        text_y = (height - text_h) / 2
        
        # Geser sedikit teks jika tombol ditekan (efek 'pressed')
        if self.is_pressed:
            text_x += 1
            text_y += 1

        gc.DrawText(self.label, text_x, text_y)


# --- CONTOH PENGGUNAAN ---
class DemoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom wx.Control Button Demo", size=(400, 300))
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(245, 245, 245))

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Inisialisasi Custom Button
        self.btn_custom = CustomButton(panel, label="Klik Saya!")
        
        # Bind event klik persis seperti wx.Button biasa
        self.btn_custom.Bind(wx.EVT_BUTTON, self.on_custom_click)

        sizer.Add(self.btn_custom, 0, wx.ALL | wx.CENTER, 50)
        panel.SetSizer(sizer)
        self.Show()

    def on_custom_click(self, event):
        wx.MessageBox("Event wx.EVT_BUTTON terdeteksi dari CustomButton!", "Info")

if __name__ == '__main__':
    app = wx.App()
    DemoFrame()
    app.MainLoop()