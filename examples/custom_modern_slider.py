import wx

# Define Custom Event untuk Slider
wxEVT_CUSTOM_SLIDER = wx.NewEventType()
EVT_CUSTOM_SLIDER = wx.PyEventBinder(wxEVT_CUSTOM_SLIDER, 1)

class CustomSliderEvent(wx.PyCommandEvent):
    def __init__(self, evtType, id, value):
        super().__init__(evtType, id)
        self.value = value

    def GetValue(self):
        return self.value


class ModernSlider(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, value=5.0, min_val=0.0, max_val=10.0,
                 pos=wx.DefaultPosition, size=(350, 60), style=wx.BORDER_NONE):
        super().__init__(parent, id, pos, size, style)

        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.value = float(max(self.min_val, min(value, self.max_val)))

        # State & Styling Params
        self.is_dragging = False
        self.is_hovered = False

        self.track_height = 8
        self.thumb_radius = 10
        self.padding_x = 20  # Space left/right for thumb to stay in control bounds

        # Colors (Modern Palette)
        self.bg_color = wx.Colour(255, 255, 255)
        self.track_bg = wx.Colour(220, 224, 230)
        self.track_active = wx.Colour(99, 102, 241)     # Modern Indigo
        self.thumb_color = wx.Colour(255, 255, 255)
        self.thumb_border = wx.Colour(99, 102, 241)
        self.tick_color = wx.Colour(160, 165, 175)
        self.text_color = wx.Colour(100, 110, 120)

        # Event Bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None) # Prevent flicker
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()

        # Background
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.GetParent().GetBackgroundColour())))
        gc.SetPen(gc.CreatePen(wx.NullPen))
        gc.DrawRectangle(0, 0, w, h)

        track_y = 20
        usable_width = w - (2 * self.padding_x)

        # 1. Draw Inactive Track
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.track_bg)))
        gc.DrawRoundedRectangle(self.padding_x, track_y - (self.track_height / 2),
                                 usable_width, self.track_height, self.track_height / 2)

        # Calculate Thumb X Position
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        thumb_x = self.padding_x + (ratio * usable_width)

        # 2. Draw Active Track (Fill)
        if ratio > 0:
            gc.SetBrush(gc.CreateBrush(wx.Brush(self.track_active)))
            gc.DrawRoundedRectangle(self.padding_x, track_y - (self.track_height / 2),
                                     thumb_x - self.padding_x, self.track_height, self.track_height / 2)

        # 3. Draw Ticks & Labels (0 to 10)
        gc.SetFont(self.GetFont().MakeSmaller(), self.text_color)
        for i in range(int(self.min_val), int(self.max_val) + 1):
            tick_ratio = (i - self.min_val) / (self.max_val - self.min_val)
            tick_x = self.padding_x + (tick_ratio * usable_width)
            tick_y1 = track_y + 10
            tick_y2 = tick_y1 + 4

            # Draw Tick Line
            gc.SetPen(gc.CreatePen(wx.Pen(self.tick_color, 1)))
            gc.StrokeLine(tick_x, tick_y1, tick_x, tick_y2)

            # Draw Label
            lbl = str(i)
            text_w, _ = gc.GetTextExtent(lbl)
            gc.DrawText(lbl, tick_x - (text_w / 2), tick_y2 + 2)

        # 4. Draw Thumb (Pegangan Slider)
        r = self.thumb_radius
        if self.is_dragging:
            r += 2  # Perbesar saat di-drag
        elif self.is_hovered:
            r += 1  # Perbesar sedikit saat hover

        # Draw Thumb Shadow
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour(0, 0, 0, 30))))
        gc.DrawEllipse(thumb_x - r, track_y - r + 2, r * 2, r * 2)

        # Draw Thumb Body
        gc.SetBrush(gc.CreateBrush(wx.Brush(self.thumb_color)))
        gc.SetPen(gc.CreatePen(wx.Pen(self.thumb_border, 3 if not self.is_dragging else 4)))
        gc.DrawEllipse(thumb_x - r, track_y - r, r * 2, r * 2)

    def _update_val_from_mouse(self, mouse_x):
        w, _ = self.GetClientSize()
        usable_width = w - (2 * self.padding_x)
        
        # Clamp x ke dalam batas usable track
        clamped_x = max(self.padding_x, min(mouse_x, w - self.padding_x))
        ratio = (clamped_x - self.padding_x) / usable_width
        
        new_val = self.min_val + (ratio * (self.max_val - self.min_val))
        
        # Jika ingin menyalakan snap ke angka bulat, hilangkan komentar baris bawah ini:
        # new_val = round(new_val)

        if new_val != self.value:
            self.value = new_val
            self.Refresh()
            self._post_event()

    def _post_event(self):
        evt = CustomSliderEvent(wxEVT_CUSTOM_SLIDER, self.GetId(), self.value)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def on_mouse_down(self, event):
        self.is_dragging = True
        self.CaptureMouse()
        self._update_val_from_mouse(event.GetX())

    def on_mouse_up(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        self.is_dragging = False
        self.Refresh()

    def on_mouse_move(self, event):
        x, y = event.GetPosition()
        self.is_hovered = True

        if self.is_dragging and event.LeftIsDown():
            self._update_val_from_mouse(x)
        else:
            self.Refresh()

    def on_mouse_leave(self, event):
        self.is_hovered = False
        self.Refresh()

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def GetValue(self):
        return self.value

    def SetValue(self, val):
        self.value = float(max(self.min_val, min(val, self.max_val)))
        self.Refresh()


# --- DEMO APPLICATION ---
class DemoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Modern wxPython Custom Slider", size=(450, 250))
        self.SetBackgroundColour(wx.Colour(248, 250, 252))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Label Nilai Current
        self.label = wx.StaticText(panel, label="Nilai Slider: 5.00", style=wx.ALIGN_CENTER)
        font = self.label.GetFont()
        font.SetPointSize(12)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.label.SetFont(font)

        # Custom Slider
        self.slider = ModernSlider(panel, value=5.0, min_val=0.0, max_val=10.0, size=(-1, 65))
        self.slider.Bind(EVT_CUSTOM_SLIDER, self.on_slider_change)

        sizer.AddStretchSpacer()
        sizer.Add(self.label, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self.slider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)
        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)
        self.Center()

    def on_slider_change(self, event):
        val = event.GetValue()
        self.label.SetLabel(f"Nilai Slider: {val:.2f}")


if __name__ == "__main__":
    app = wx.App()
    frame = DemoFrame()
    frame.Show()
    app.MainLoop()