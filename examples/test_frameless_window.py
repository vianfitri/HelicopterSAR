import wx

class CustomTitleBar(wx.Panel):
    """Titlebar kustom dengan fitur Drag, Double Click Maximize, dan Drag-to-Snap."""
    def __init__(self, parent, title="Custom Window"):
        super().__init__(parent)
        self.parent = parent
        self.SetBackgroundColour(wx.Colour(15, 25, 42))

        self._drag_start_pos = wx.Point(0, 0)
        self._is_dragging = False

        # Sizer utama titlebar
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Judul Window
        self.title_text = wx.StaticText(self, label=f"  {title}")
        self.title_text.SetForegroundColour(wx.Colour(220, 220, 220))
        font = self.title_text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.title_text.SetFont(font)
        sizer.Add(self.title_text, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # Tombol Minimize
        btn_min = wx.Button(self, label="—", size=(30, 25), style=wx.BORDER_NONE)
        btn_min.SetBackgroundColour(wx.Colour(35, 50, 75))
        btn_min.SetForegroundColour(wx.Colour(255, 255, 255))
        btn_min.Bind(wx.EVT_BUTTON, self.on_minimize)
        sizer.Add(btn_min, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)

        # Tombol Maximize / Restore
        self.btn_max = wx.Button(self, label="🗖", size=(30, 25), style=wx.BORDER_NONE)
        self.btn_max.SetBackgroundColour(wx.Colour(35, 50, 75))
        self.btn_max.SetForegroundColour(wx.Colour(255, 255, 255))
        self.btn_max.Bind(wx.EVT_BUTTON, self.on_maximize_toggle)
        sizer.Add(self.btn_max, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)

        # Tombol Close
        btn_close = wx.Button(self, label="✕", size=(30, 25), style=wx.BORDER_NONE)
        btn_close.SetBackgroundColour(wx.Colour(180, 40, 40))
        btn_close.SetForegroundColour(wx.Colour(255, 255, 255))
        btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        sizer.Add(btn_close, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

        self.SetSizer(sizer)

        # Bind event mouse ke titlebar dan text judul
        for widget in (self, self.title_text):
            widget.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
            widget.Bind(wx.EVT_LEFT_UP, self.on_left_up)
            widget.Bind(wx.EVT_MOTION, self.on_mouse_move)
            widget.Bind(wx.EVT_LEFT_DCLICK, self.on_maximize_toggle)

    def on_left_down(self, event):
        widget = event.GetEventObject()
        if not widget.HasCapture():
            widget.CaptureMouse()

        self._is_dragging = True
        top_frame = self.GetTopLevelParent()
        self._drag_start_pos = wx.GetMousePosition() - top_frame.GetPosition()

    def on_mouse_move(self, event):
        widget = event.GetEventObject()
        if event.Dragging() and event.LeftIsDown() and widget.HasCapture() and self._is_dragging:
            top_frame = self.GetTopLevelParent()
            
            # Jika di-drag saat keadaan Maximize, un-maximize secara otomatis
            if top_frame.is_maximized:
                top_frame.restore_if_maximized()
                self._drag_start_pos = wx.Point(top_frame.GetSize().width // 2, 15)

            current_mouse_pos = wx.GetMousePosition()
            top_frame.Move(current_mouse_pos - self._drag_start_pos)

    def on_left_up(self, event):
        widget = event.GetEventObject()
        if widget.HasCapture():
            widget.ReleaseMouse()

        if not self._is_dragging:
            return

        self._is_dragging = False
        top_frame = self.GetTopLevelParent()
        mouse_pos = wx.GetMousePosition()

        # Dapatkan spesifikasi area kerja monitor aktif
        display_idx = wx.Display.GetFromPoint(mouse_pos)
        if display_idx == wx.NOT_FOUND:
            display_idx = 0
        display = wx.Display(display_idx)
        work_area = display.GetClientArea()

        # Jarak toleransi snap (semakin besar semakin mudah terkejar ke pinggir)
        snap_margin = 25 

        # --- LOGIKA SNAP WINDOW ---
        # 1. Snap Ke Tepi Atas -> Maximize Fullscreen
        if mouse_pos.y <= work_area.y + snap_margin:
            top_frame.maximize_window()

        # 2. Snap Ke Tepi Kiri -> Half Screen Kiri
        elif mouse_pos.x <= work_area.x + snap_margin:
            top_frame.restore_if_maximized()
            half_width = work_area.width // 2
            top_frame.SetSize(work_area.x, work_area.y, half_width, work_area.height)
            top_frame.Layout()

        # 3. Snap Ke Tepi Kanan -> Half Screen Kanan
        elif mouse_pos.x >= (work_area.x + work_area.width - snap_margin):
            top_frame.restore_if_maximized()
            half_width = work_area.width // 2
            top_frame.SetSize(work_area.x + half_width, work_area.y, half_width, work_area.height)
            top_frame.Layout()

    def on_minimize(self, event):
        self.GetTopLevelParent().Iconize(True)

    def on_maximize_toggle(self, event):
        top_frame = self.GetTopLevelParent()
        if top_frame.is_maximized:
            top_frame.restore_if_maximized()
        else:
            top_frame.maximize_window()

    def on_close(self, event):
        self.GetTopLevelParent().Close()

    def update_max_button_icon(self, is_maximized):
        self.btn_max.SetLabel("🗗" if is_maximized else "🗖")


class CustomWindow(wx.Frame):
    """Main Frame Frameless dengan Custom Titlebar, Snap, dan Resizing."""
    def __init__(self):
        super().__init__(
            None, 
            title="Helicopter SAR", 
            size=(700, 450), 
            style=wx.BORDER_NONE | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX
        )

        self.is_maximized = False
        self._normal_rect = self.GetRect()

        self.dark_slate_navy = wx.Colour(20, 32, 53)
        self.SetBackgroundColour(self.dark_slate_navy)

        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour(self.dark_slate_navy)

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # 1. TitleBar
        self.title_bar = CustomTitleBar(self.main_panel, title="Helicopter SAR - Control Panel")
        panel_sizer.Add(self.title_bar, 0, wx.EXPAND)

        # 2. Area Konten
        content_sizer = wx.BoxSizer(wx.VERTICAL)
        welcome_msg = wx.StaticText(
            self.main_panel, 
            label="Custom Window wxPython\nBackground: DarkSlateNavy\n\nCara Coba Snap:\nDrag titlebar hingga kursor menyentuh paling atas/kiri/kanan monitor, lalu LEPAS MOUSE!"
        )
        welcome_msg.SetForegroundColour(wx.Colour(220, 230, 240))
        font = welcome_msg.GetFont()
        font.SetPointSize(11)
        welcome_msg.SetFont(font)

        content_sizer.Add(welcome_msg, 0, wx.ALL, 25)
        panel_sizer.Add(content_sizer, 1, wx.EXPAND)

        # 3. Bottom Bar & Resize Handle
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.resize_grip = wx.StaticText(self.main_panel, label="◢  ")
        self.resize_grip.SetForegroundColour(wx.Colour(120, 140, 170))
        self.resize_grip.SetCursor(wx.Cursor(wx.CURSOR_SIZENWSE))
        
        self.resize_grip.Bind(wx.EVT_LEFT_DOWN, self.on_resize_start)
        self.resize_grip.Bind(wx.EVT_LEFT_UP, self.on_resize_end)
        self.resize_grip.Bind(wx.EVT_MOTION, self.on_resizing)

        bottom_sizer.AddStretchSpacer(1)
        bottom_sizer.Add(self.resize_grip, 0, wx.ALIGN_BOTTOM | wx.ALL, 3)

        panel_sizer.Add(bottom_sizer, 0, wx.EXPAND)

        self.main_panel.SetSizer(panel_sizer)
        frame_sizer.Add(self.main_panel, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

        self.Layout()
        self.Refresh()
        self.Center()

    def maximize_window(self):
        if not self.is_maximized:
            self._normal_rect = self.GetRect()
            display = wx.Display(wx.Display.GetFromWindow(self))
            work_area = display.GetClientArea()
            
            self.SetSize(work_area)
            self.is_maximized = True
            self.title_bar.update_max_button_icon(True)
            self.resize_grip.Hide()
            self.Layout()

    def restore_if_maximized(self):
        if self.is_maximized:
            self.SetRect(self._normal_rect)
            self.is_maximized = False
            self.title_bar.update_max_button_icon(False)
            self.resize_grip.Show()
            self.Layout()

    def on_resize_start(self, event):
        if not self.is_maximized:
            self._resize_start_pos = wx.GetMousePosition()
            self._initial_size = self.GetSize()
            if not self.resize_grip.HasCapture():
                self.resize_grip.CaptureMouse()

    def on_resize_end(self, event):
        if self.resize_grip.HasCapture():
            self.resize_grip.ReleaseMouse()

    def on_resizing(self, event):
        if event.Dragging() and event.LeftIsDown() and self.resize_grip.HasCapture():
            curr_pos = wx.GetMousePosition()
            diff = curr_pos - self._resize_start_pos
            new_width = max(400, self._initial_size.width + diff.x)
            new_height = max(250, self._initial_size.height + diff.y)
            self.SetSize((new_width, new_height))
            self.Layout()
            self.Refresh()


if __name__ == "__main__":
    app = wx.App()
    win = CustomWindow()
    win.Show()
    app.MainLoop()