import wx

class ModernButton(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, label="", icon=None, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name="ModernButton",
                 # --- Parameters ---
                 bg_color="#3B82F6",
                 hover_color="#2563EB",
                 click_color="#1D4ED8",
                 border_color="#1E40AF",
                 text_color="#FFFFFF",
                 disabled_bg_color="#D1D5DB",
                 disabled_text_color="#9CA3AF",
                 border_radius=8,
                 border_width=1,
                 shadow=True,
                 shadow_color="#1E293B33", # Hex dengan alpha (RGBA)
                 icon_size=(20, 20),
                 spacing=8,
                 icon_position="left",    # 'left', 'right', 'top', 'bottom'
                 text_align="center",     # 'left', 'center', 'right'
                 animate_hover=True
                 ):
        
        super().__init__(parent, id, pos, size, style | wx.BORDER_NONE, validator, name)

        # Content Props
        self._label = label
        self._icon = icon
        
        # Color Props (Hex string or wx.Colour)
        self._bg_color = wx.Colour(bg_color)
        self._hover_color = wx.Colour(hover_color)
        self._click_color = wx.Colour(click_color)
        self._border_color = wx.Colour(border_color)
        self._text_color = wx.Colour(text_color)
        self._disabled_bg_color = wx.Colour(disabled_bg_color)
        self._disabled_text_color = wx.Colour(disabled_text_color)
        self._shadow_color = wx.Colour(shadow_color)
        
        # Layout & Style Props
        self.border_radius = border_radius
        self.border_width = border_width
        self.shadow = shadow
        self.icon_size = icon_size
        self.spacing = spacing
        self.icon_position = icon_position.lower()
        self.text_align = text_align.lower()
        self.animate_hover = animate_hover

        # State management
        self._is_hovered = False
        self._is_pressed = False
        self._current_bg = wx.Colour(self._bg_color)
        self._target_bg = wx.Colour(self._bg_color)

        # Animation Timer setup
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_animate_step, self._timer)

        # Event Bindings
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None) # Prevents flicker

        # Set double buffering for smooth rendering
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        # Auto-scale initial size if DefaultSize passed
        self.SetInitialSize(size)

    # --- Sizer Integration & Layout Calculation ---
    def DoGetBestSize(self):
        """Menghitung ukuran ideal button agar mendukung Sizer secara otomatis."""
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        
        text_w, text_h = dc.GetTextExtent(self._label) if self._label else (0, 0)
        
        icon_w, icon_h = 0, 0
        if self._icon and self._icon.IsOk():
            icon_w, icon_h = self.icon_size

        padding_x, padding_y = 16, 10
        
        if self.icon_position in ("left", "right"):
            content_w = text_w + icon_w + (self.spacing if text_w and icon_w else 0)
            content_h = max(text_h, icon_h)
        else: # 'top', 'bottom'
            content_w = max(text_w, icon_w)
            content_h = text_h + icon_h + (self.spacing if text_h and icon_h else 0)

        best_w = content_w + (padding_x * 2) + (self.border_width * 2)
        best_h = content_h + (padding_y * 2) + (self.border_width * 2)
        
        if self.shadow:
            best_w += 2
            best_h += 4

        return wx.Size(max(best_w, 80), max(best_h, 32))

    # --- Event Handlers & Animation ---
    def _on_enter(self, event):
        if self.IsEnabled():
            self._is_hovered = True
            self._start_color_transition(self._hover_color)
        event.Skip()

    def _on_leave(self, event):
        if self.IsEnabled():
            self._is_hovered = False
            self._is_pressed = False
            self._start_color_transition(self._bg_color)
        event.Skip()

    def _on_left_down(self, event):
        if self.IsEnabled():
            self._is_pressed = True
            self._current_bg = wx.Colour(self._click_color)
            self.Refresh()
        event.Skip()

    def _on_left_up(self, event):
        if self.IsEnabled() and self._is_pressed:
            self._is_pressed = False
            self._current_bg = self._hover_color if self._is_hovered else self._bg_color
            self.Refresh()
            
            # Emit standard wx.EVT_BUTTON event
            btn_evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            btn_evt.SetEventObject(self)
            self.ProcessWindowEvent(btn_evt)
        event.Skip()

    def _start_color_transition(self, target_color):
        if not self.animate_hover:
            self._current_bg = wx.Colour(target_color)
            self.Refresh()
            return
            
        self._target_bg = wx.Colour(target_color)
        if not self._timer.IsRunning():
            self._timer.Start(15) # ~60 FPS update interval

    def _on_animate_step(self, event):
        # Interpolasi linier (LERP) antar warna
        r = self._current_bg.Red() + (self._target_bg.Red() - self._current_bg.Red()) * 0.2
        g = self._current_bg.Green() + (self._target_bg.Green() - self._current_bg.Green()) * 0.2
        b = self._current_bg.Blue() + (self._target_bg.Blue() - self._current_bg.Blue()) * 0.2
        
        self._current_bg = wx.Colour(int(r), int(g), int(b))
        self.Refresh()

        # Stop timer jika warna sudah hampir sama dengan target
        if abs(self._current_bg.Red() - self._target_bg.Red()) < 2 and \
           abs(self._current_bg.Green() - self._target_bg.Green()) < 2 and \
           abs(self._current_bg.Blue() - self._target_bg.Blue()) < 2:
            self._current_bg = wx.Colour(self._target_bg)
            self._timer.Stop()
            self.Refresh()

    # --- Drawing Logic ---
    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
        width, height = self.GetClientSize()

        # Canvas positioning offset when pressed
        press_offset = 1 if self._is_pressed else 0
        shadow_offset = 3 if self.shadow and not self._is_pressed else 0

        rect_x = self.border_width
        rect_y = self.border_width + press_offset
        rect_w = width - (self.border_width * 2)
        rect_h = height - (self.border_width * 2) - shadow_offset

        # 1. Draw Shadow (If Enabled)
        if self.shadow and self.IsEnabled():
            gc.SetBrush(gc.CreateBrush(wx.Brush(self._shadow_color)))
            gc.SetPen(wx.NullPen)
            gc.DrawRoundedRectangle(
                rect_x, rect_y + 2, rect_w, rect_h, self.border_radius
            )

        # 2. Draw Main Background & Border
        if not self.IsEnabled():
            bg_col = self._disabled_text_color
            border_col = self._disabled_bg_color
        else:
            bg_col = self._current_bg
            border_col = self._border_color

        gc.SetBrush(gc.CreateBrush(wx.Brush(bg_col)))
        gc.SetPen(gc.CreatePen(wx.Pen(border_col, self.border_width)))
        gc.DrawRoundedRectangle(rect_x, rect_y, rect_w, rect_h, self.border_radius)

        # 3. Render Icon & Text
        self._draw_content(gc, rect_x, rect_y, rect_w, rect_h)

    def _draw_content(self, gc, x, y, w, h):
        # 1. Set Font pada GraphicsContext TERLEBIH DAHULU sebelum GetTextExtent
        txt_color = self._disabled_text_color if not self.IsEnabled() else self._text_color
        gc.SetFont(self.GetFont(), txt_color)

        # 2. Sekarang GetTextExtent aman dipanggil
        text_w, text_h = gc.GetTextExtent(self._label) if self._label else (0, 0)
        
        has_icon = self._icon and self._icon.IsOk()
        icon_w, icon_h = self.icon_size if has_icon else (0, 0)

        # Scale Icon Bitmap
        scaled_icon = None
        if has_icon:
            img = self._icon.ConvertToImage()
            img = img.Scale(icon_w, icon_h, wx.IMAGE_QUALITY_HIGH)
            scaled_icon = wx.Bitmap(img)

        # Calculate Positions
        if self.icon_position in ("left", "right"):
            total_w = text_w + icon_w + (self.spacing if text_w and icon_w else 0)
            
            # Text Align Horizontal Offset
            if self.text_align == "left":
                start_x = x + 12
            elif self.text_align == "right":
                start_x = x + w - total_w - 12
            else: # Center
                start_x = x + (w - total_w) / 2

            if self.icon_position == "left":
                icon_x = start_x
                text_x = start_x + icon_w + (self.spacing if icon_w else 0)
            else: # right
                text_x = start_x
                icon_x = start_x + text_w + (self.spacing if text_w else 0)

            icon_y = y + (h - icon_h) / 2
            text_y = y + (h - text_h) / 2

        else: # 'top', 'bottom'
            total_h = text_h + icon_h + (self.spacing if text_h and icon_h else 0)
            start_y = y + (h - total_h) / 2

            if self.icon_position == "top":
                icon_y = start_y
                text_y = start_y + icon_h + (self.spacing if icon_h else 0)
            else: # bottom
                text_y = start_y
                icon_y = start_y + text_h + (self.spacing if text_h else 0)

            icon_x = x + (w - icon_w) / 2
            text_x = x + (w - text_w) / 2

        # Draw Icon
        if scaled_icon:
            gc.DrawBitmap(scaled_icon, icon_x, icon_y, icon_w, icon_h)

        # Draw Text (Font sudah di-set di atas)
        if self._label:
            gc.DrawText(self._label, text_x, text_y)

    # --- Getters & Setters ---
    def SetLabel(self, label):
        self._label = label
        self.InvalidateBestSize()
        self.Refresh()

    def SetIcon(self, icon):
        self._icon = icon
        self.InvalidateBestSize()
        self.Refresh()

class DemoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Control ModernButton Demo", size=(450, 400))
        self.SetBackgroundColour("#F8FAFC")

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # 1. Modern Button standar dengan Icon di kiri
        btn_icon = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_BUTTON, (32, 32))
        btn1 = ModernButton(
            panel, label="Primary Action", icon=btn_icon,
            bg_color="#0ea5e9", hover_color="#0284c7", click_color="#0369a1",
            border_radius=12, shadow=True, icon_size=(20, 20)
        )
        btn1.Bind(wx.EVT_BUTTON, lambda e: wx.MessageBox("Primary Clicked!"))

        # 2. Button Danger (Icon di Kanan, Corner Radius besar)
        btn2 = ModernButton(
            panel, label="Delete Item", icon=btn_icon,
            bg_color="#ef4444", hover_color="#dc2626", click_color="#b91c1c",
            border_color="#991b1b", border_radius=20, icon_position="right",
            shadow=True
        )

        # 3. Button Icon Atas (Top Position)
        btn3 = ModernButton(
            panel, label="Download", icon=btn_icon,
            bg_color="#10b981", hover_color="#059669", click_color="#047857",
            border_radius=8, icon_position="top", icon_size=(24, 24), spacing=4
        )

        # Add components to Sizer
        sizer.Add(btn1, 0, wx.ALL | wx.CENTER, 10)
        sizer.Add(btn2, 0, wx.ALL | wx.CENTER, 10)
        sizer.Add(btn3, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(sizer)
        self.Centre()

if __name__ == "__main__":
    app = wx.App()
    frame = DemoFrame()
    frame.Show()
    app.MainLoop()