import wx

import wx

class RoundedTabButtonCtl(wx.Control):
    def __init__(self, parent, tab_id, label, icon_char="", active=False):
        super().__init__(parent, style=wx.BORDER_NONE)
        
        self.tab_id = tab_id
        self.label = label
        self.icon_char = icon_char
        self.is_active = active
        self.is_hovered = False

        # 1. Izinkan komponen menerima fokus dari Keyboard (Tombol TAB)
        self.SetCanFocus(True)
        self.SetMinSize((180, 45))
        
        # Event Bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_hover_leave)
        
        # Event untuk Indikator Fokus Keyboard
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus_change)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_focus_change)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

    def set_active(self, active):
        self.is_active = active
        self.Refresh()

    def on_hover_enter(self, event):
        self.is_hovered = True
        self.Refresh()

    def on_hover_leave(self, event):
        self.is_hovered = False
        self.Refresh()

    def on_focus_change(self, event):
        self.Refresh()
        event.Skip()

    def on_key_down(self, event):
        # Eksekusi tombol saat ditekan SPACE atau ENTER melalui Keyboard
        if event.GetKeyCode() in (wx.WXK_SPACE, wx.WXK_RETURN):
            self.trigger_click_event()
        else:
            event.Skip()

    def on_click(self, event):
        self.SetFocus()  # Ambil fokus saat diklik mouse
        self.trigger_click_event()

    def trigger_click_event(self):
        # Memicu wx.CommandEvent tipe EVT_BUTTON standar
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        rect = self.GetClientRect()
        padding = 4
        btn_rect = wx.Rect(
            rect.x + padding, 
            rect.y + padding, 
            rect.width - (padding * 2), 
            rect.height - (padding * 2)
        )

        # Skema Warna
        if self.is_active:
            bg_color = wx.Colour(41, 128, 185)   # Biru Aktif
            text_color = wx.Colour(255, 255, 255)
        elif self.is_hovered:
            bg_color = wx.Colour(235, 240, 245) # Hover
            text_color = wx.Colour(40, 40, 40)
        else:
            bg_color = wx.Colour(245, 245, 245) # Default
            text_color = wx.Colour(100, 100, 100)

        # Menggambar Background Rounded Rectangle
        gc.SetBrush(gc.CreateBrush(wx.Brush(bg_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(bg_color, 1)))
        
        radius = 12.0
        path = gc.CreatePath()
        path.AddRoundedRectangle(btn_rect.x, btn_rect.y, btn_rect.width, btn_rect.height, radius)
        gc.FillPath(path)

        # Draw Outline Indikator Fokus Keyboard (Dotted Border jika sedang aktif di-TAB)
        if self.HasFocus():
            focus_pen = wx.Pen(wx.Colour(41, 128, 185), 1, wx.PENSTYLE_SHORT_DASH)
            gc.SetPen(gc.CreatePen(focus_pen))
            gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0,0,0,0)))) # Transparan
            gc.StrokePath(path)

        # Menggambar Teks
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                       wx.FONTWEIGHT_BOLD if self.is_active else wx.FONTWEIGHT_NORMAL)
        gc.SetFont(font, text_color)

        display_text = f"{self.icon_char}  {self.label}".strip()
        w, h = gc.GetTextExtent(display_text)
        text_x = btn_rect.x + 15
        text_y = btn_rect.y + (btn_rect.height - h) / 2
        gc.DrawText(display_text, text_x, text_y)

class RoundedTabButton(wx.Panel):
    def __init__(self, parent, tab_id, label, icon_char="", active=False, callback=None):
        super().__init__(parent)
        self.tab_id = tab_id
        self.label = label
        self.icon_char = icon_char
        self.is_active = active
        self.callback = callback
        self.is_hovered = False

        self.SetMinSize((180, 45))
        
        # Event Bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_hover_leave)
        
        # Mengurangi flicker saat rendering
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

    def set_active(self, active):
        self.is_active = active
        self.Refresh()

    def on_hover_enter(self, event):
        self.is_hovered = True
        self.Refresh()

    def on_hover_leave(self, event):
        self.is_hovered = False
        self.Refresh()

    def on_click(self, event):
        if self.callback:
            self.callback(self.tab_id)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        # Menggunakan GraphicsContext untuk antialiasing & rounded rectangle yang mulus
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        rect = self.GetClientRect()
        # Berikan sedikit margin di sekitar button
        padding = 4
        btn_rect = wx.Rect(
            rect.x + padding, 
            rect.y + padding, 
            rect.width - (padding * 2), 
            rect.height - (padding * 2)
        )

        # Skema Warna
        if self.is_active:
            bg_color = wx.Colour(41, 128, 185)   # Biru Aktif
            text_color = wx.Colour(255, 255, 255) # Teks Putih
        elif self.is_hovered:
            bg_color = wx.Colour(235, 240, 245) # Abu-abu Hover
            text_color = wx.Colour(40, 40, 40)
        else:
            bg_color = wx.Colour(245, 245, 245) # Default Transparan/Terang
            text_color = wx.Colour(100, 100, 100)

        # Menggambar Background Rounded Rectangle
        gc.SetBrush(gc.CreateBrush(wx.Brush(bg_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(bg_color, 1)))
        
        radius = 12.0 # Tingkat kebulatan sudut
        path = gc.CreatePath()
        path.AddRoundedRectangle(btn_rect.x, btn_rect.y, btn_rect.width, btn_rect.height, radius)
        gc.FillPath(path)

        # Menggambar Teks/Label
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                       wx.FONTWEIGHT_BOLD if self.is_active else wx.FONTWEIGHT_NORMAL)
        gc.SetFont(font, text_color)

        display_text = f"{self.icon_char}  {self.label}".strip()
        
        # Posisi Teks di Tengah Vertikal
        w, h = gc.GetTextExtent(display_text)
        text_x = btn_rect.x + 15
        text_y = btn_rect.y + (btn_rect.height - h) / 2
        gc.DrawText(display_text, text_x, text_y)


class CustomSidebarTabControl(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.tabs = []
        self.pages = {}
        self.active_tab_id = None

        # Layout Utama: Horizontal (Sidebar kiri, Konten kanan)
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Sidebar Sizer
        self.sidebar_panel = wx.Panel(self)
        self.sidebar_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.sidebar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sidebar_panel.SetSizer(self.sidebar_sizer)

        # Container Konten Halaman (Kanan)
        self.content_panel = wx.Panel(self)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)

        # Susun Layout Utama
        self.main_sizer.Add(self.sidebar_panel, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.EXPAND)
        self.main_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        self.SetSizer(self.main_sizer)

    def add_tab(self, tab_id, label, page_panel, icon_char=""):
        # Menyimpan halaman konten (Sembunyikan dulu secara default)
        page_panel.Reparent(self.content_panel)
        page_panel.Hide()
        self.content_sizer.Add(page_panel, 1, wx.EXPAND)
        self.pages[tab_id] = page_panel

        # Buat Tab Button kustom
        is_first = len(self.tabs) == 0
        tab_btn = RoundedTabButton(
            self.sidebar_panel, 
            tab_id=tab_id, 
            label=label, 
            icon_char=icon_char,
            active=is_first,
            callback=self.on_tab_change
        )
        
        self.sidebar_sizer.Add(tab_btn, 0, wx.EXPAND | wx.BOTTOM, 4)
        self.tabs.append(tab_btn)

        if is_first:
            self.active_tab_id = tab_id
            page_panel.Show()

        self.Layout()

    def on_tab_change(self, tab_id):
        if tab_id == self.active_tab_id:
            return

        # Sembunyikan halaman lama & tampilkan halaman baru
        self.pages[self.active_tab_id].Hide()
        self.pages[tab_id].Show()
        self.active_tab_id = tab_id

        # Update status visual tombol tab
        for btn in self.tabs:
            btn.set_active(btn.tab_id == tab_id)

        self.content_panel.Layout()


# --- CONTOH PENGGUNAAN ---
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Sidebar Tab Control", size=(700, 450))
        self.SetBackgroundColour(wx.Colour(240, 240, 240))

        # Buat Tab Control
        tab_control = CustomSidebarTabControl(self)

        # Halaman 1
        page1 = wx.Panel(tab_control)
        page1.SetBackgroundColour(wx.Colour(255, 255, 255))
        wx.StaticText(page1, label="Halaman Dashboard", pos=(20, 20))

        # Halaman 2
        page2 = wx.Panel(tab_control)
        page2.SetBackgroundColour(wx.Colour(255, 255, 255))
        wx.StaticText(page2, label="Halaman Profil / User", pos=(20, 20))

        # Halaman 3
        page3 = wx.Panel(tab_control)
        page3.SetBackgroundColour(wx.Colour(255, 255, 255))
        wx.StaticText(page3, label="Halaman Pengaturan (Settings)", pos=(20, 20))

        # Tambahkan Tab
        tab_control.add_tab("dashboard", "Dashboard", page1, icon_char="📊")
        tab_control.add_tab("profile", "Profile", page2, icon_char="👤")
        tab_control.add_tab("settings", "Settings", page3, icon_char="⚙️")

        self.Centre()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()