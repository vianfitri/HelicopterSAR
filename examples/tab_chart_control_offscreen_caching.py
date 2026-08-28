import wx
import bisect

# --- Konstanta Warna ---
COLOR_BG = wx.Colour(19, 23, 31) 
COLOR_TAB_UNSELECTED = wx.Colour(160, 160, 160)
COLOR_ORANGE_GLOW = wx.Colour(255, 140, 0) # Safety Orange Menyala
COLOR_ORANGE_LINE = wx.Colour(255, 100, 0)
COLOR_BLUE = wx.Colour(50, 160, 255)
COLOR_HOVER_POPUP = wx.Colour(25, 29, 39, 230)

class CustomTabControl(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER, tabs=[]):
        super().__init__(parent, id, pos, size, style)
        
        self.tabs = tabs
        self.selected_index = 0
        self.padding_h = 20
        self.padding_v = 10
        self.gap = 2

        self.SetBackgroundColour(COLOR_BG)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    def SetTabs(self, tabs):
        self.tabs = tabs
        self.selected_index = 0
        self.Refresh()

    def GetSelectedIndex(self):
        return self.selected_index

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(COLOR_BG))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.GetClientSize()
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)

        current_x = self.padding_h
        tab_h = h - self.padding_v * 2

        font_selected = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font_unselected = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        for i, tab_label in enumerate(self.tabs):
            text_w, text_h = dc.GetTextExtent(tab_label)
            tab_w = text_w + self.padding_h * 1.5

            tab_rect = wx.Rect(current_x, self.padding_v, int(tab_w), int(tab_h))

            c1 = wx.Colour(45, 50, 60)
            c2 = COLOR_BG
            
            if i == self.selected_index:
                # Gradasi Latar Belakang Tab Terpilih
                path = gc.CreatePath()
                path.AddRoundedRectangle(tab_rect.x, tab_rect.y, tab_rect.width, tab_rect.height, 4)
                
                brush = gc.CreateLinearGradientBrush(tab_rect.x, tab_rect.y, tab_rect.x, tab_rect.bottom, c1, c2)
                gc.SetBrush(brush)
                gc.FillPath(path)

                # Garis Bawah Safety Orange Menyala
                line_y = tab_rect.bottom - 4
                line_w = tab_rect.width
                line_x = tab_rect.x
                
                glow_gc = wx.GraphicsContext.Create(dc)
                glow_gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
                
                glow_gc.SetBrush(wx.Brush(COLOR_ORANGE_GLOW.ChangeLightness(130)))
                glow_gc.DrawRectangle(line_x - 1, line_y - 1, line_w + 2, 6)
                glow_gc.SetBrush(wx.Brush(COLOR_ORANGE_GLOW.ChangeLightness(150)))
                glow_gc.DrawRectangle(line_x - 2, line_y - 2, line_w + 4, 8)

                gc.SetBrush(wx.Brush(COLOR_ORANGE_GLOW))
                gc.DrawRectangle(line_x, line_y, line_w, 4)

                gc.SetFont(font_selected, COLOR_ORANGE_GLOW)
                text_y = tab_rect.y + (tab_rect.height - text_h) / 2
                gc.DrawText(tab_label, tab_rect.x + (tab_rect.width - text_w) / 2, text_y)

            else:
                gc.SetFont(font_unselected, COLOR_TAB_UNSELECTED)
                text_y = tab_rect.y + (tab_rect.height - text_h) / 2
                gc.DrawText(tab_label, tab_rect.x + (tab_rect.width - text_w) / 2, text_y)

            current_x += int(tab_w) + self.gap

    def OnLeftDown(self, event):
        x, y = event.GetPosition()
        current_x = self.padding_h
        dc = wx.ClientDC(self)

        for i, tab_label in enumerate(self.tabs):
            text_w, text_h = dc.GetTextExtent(tab_label)
            tab_w = text_w + self.padding_h * 1.5
            
            if current_x <= x <= current_x + tab_w:
                if self.selected_index != i:
                    self.selected_index = i
                    self.Refresh()
                    evt = wx.CommandEvent(wx.wxEVT_COMMAND_TAB_CHANGED, self.GetId())
                    evt.SetInt(i)
                    self.GetEventHandler().ProcessEvent(evt)
                break
            
            current_x += int(tab_w) + self.gap
            
        event.Skip()

wx.wxEVT_COMMAND_TAB_CHANGED = wx.NewEventType()
EVT_TAB_CHANGED = wx.PyEventBinder(wx.wxEVT_COMMAND_TAB_CHANGED, 1)

class TimelineChartControl(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER, timeline_max=300):
        super().__init__(parent, id, pos, size, style)
        self.SetBackgroundColour(COLOR_BG)

        # Mencegah flicker dengan double-buffering native
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)

        self.timeline_max = timeline_max
        self.current_time_review = -1

        self.times = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
        self.data_position = [3.2, 3.1, 3.3, 3.8, 4.3, 4.4, 4.7, 3.9, 3.5, 3.6, 4.1, 4.2, 3.0, 1.5, 1.5, 1.0]
        self.data_hoist = [1.2, 1.2, 1.5, 1.8, 2.5, 3.8, 4.5, 5.8, 7.8, 10.1, 12.0, 12.8, 11.5, 9.8, 6.5, 2.8]

        self.min_y_pos, self.max_y_pos = 0, 5
        self.min_y_hoist, self.max_y_hoist = 0, 15
        
        self.margin_left = 60
        self.margin_right = 60
        self.margin_top = 40
        self.margin_bottom = 50

        # Variable Cache Bitmap
        self._cached_bitmap = None

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

    def OnSize(self, event):
        # Batal cache bitmap saat window di-resize
        self._cached_bitmap = None
        event.Skip()

    def SetTimelineMax(self, seconds):
        self.timeline_max = seconds
        self._cached_bitmap = None
        self.Refresh()

    def FormatTime(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def GetChartCoords(self):
        w, h = self.GetClientSize()
        chart_w = w - self.margin_left - self.margin_right
        chart_h = h - self.margin_top - self.margin_bottom
        return self.margin_left, self.margin_top, chart_w, chart_h

    def WorldToClient(self, time_sec, y_value, min_y, max_y):
        cx, cy, cw, ch = self.GetChartCoords()
        x = cx + (time_sec / self.timeline_max) * cw
        norm_y = (y_value - min_y) / (max_y - min_y)
        y = cy + ch - norm_y * ch
        return x, y

    def ClientToWorldTime(self, client_x):
        cx, cy, cw, ch = self.GetChartCoords()
        if client_x < cx or client_x > cx + cw:
            return -1
        norm_x = (client_x - cx) / cw
        return norm_x * self.timeline_max

    def RebuildChartCache(self, width, height):
        """Menggambar elemen statis ke memori bitmap (Sumbu, Grid, Line Data)"""
        bitmap = wx.Bitmap(width, height)
        dc = wx.MemoryDC(bitmap)
        dc.SetBackground(wx.Brush(COLOR_BG))
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            dc.SelectObject(wx.NullBitmap)
            return bitmap

        cx, cy, cw, ch = self.GetChartCoords()
        gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)

        # 1. Sumbu & Grid
        axis_font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        gc.SetFont(axis_font, COLOR_ORANGE_GLOW.ChangeLightness(150))
        text_w, text_h = dc.GetTextExtent("0 m")
        
        for val in [0, 2.5, 5]:
            x, y = self.WorldToClient(0, val, self.min_y_pos, self.max_y_pos)
            s = f"{val} m"
            gc.DrawText(s, cx - text_w - 5, y - text_h/2)
            grid_pen = wx.Pen(wx.Colour(50, 50, 50), 1, wx.PENSTYLE_DOT)
            gc.SetPen(grid_pen)
            gc.StrokeLine(cx, y, cx + cw, y)

        gc.SetFont(axis_font, COLOR_BLUE.ChangeLightness(150))
        for val in [0, 7.5, 15]:
            x, y = self.WorldToClient(self.timeline_max, val, self.min_y_hoist, self.max_y_hoist)
            s = f"{val} m"
            tw, th = dc.GetTextExtent(s)
            gc.DrawText(s, cx + cw + 5, y - th/2)

        gc.SetFont(axis_font, COLOR_TAB_UNSELECTED)
        intervals = int(self.timeline_max // 60) + 1
        for i in range(intervals):
            time_val = i * 60
            if time_val > self.timeline_max: break
            x, y = self.WorldToClient(time_val, 0, self.min_y_pos, self.max_y_pos)
            s = self.FormatTime(time_val)
            tw, th = dc.GetTextExtent(s)
            gc.DrawText(s, x - tw/2, cy + ch + 10)
            if i > 0:
                gc.SetPen(wx.Pen(wx.Colour(50, 50, 50, 100), 1, wx.PENSTYLE_SOLID))
                gc.StrokeLine(x, cy, x, cy + ch)

        # 2. Hoist Data (Blue Line)
        path_hoist = gc.CreatePath()
        points_hoist = []
        for time, hoist_val in zip(self.times, self.data_hoist):
            x, y = self.WorldToClient(time, hoist_val, self.min_y_hoist, self.max_y_hoist)
            if not points_hoist: path_hoist.MoveToPoint(x, y)
            else: path_hoist.AddLineToPoint(x, y)
            points_hoist.append((x, y))

        gc.SetPen(wx.Pen(COLOR_BLUE, 2))
        gc.SetBrush(wx.NullBrush)
        gc.StrokePath(path_hoist)
        
        gc.SetBrush(wx.Brush(COLOR_BLUE))
        gc.SetPen(wx.NullPen)
        for x, y in points_hoist:
            gc.DrawEllipse(x - 3, y - 3, 6, 6)

        # 3. Position Data (Orange Line)
        path_position = gc.CreatePath()
        points_position = []
        for time, pos_val in zip(self.times, self.data_position):
            x, y = self.WorldToClient(time, pos_val, self.min_y_pos, self.max_y_pos)
            if not points_position: path_position.MoveToPoint(x, y)
            else: path_position.AddLineToPoint(x, y)
            points_position.append((x, y))

        gc.SetPen(wx.Pen(COLOR_ORANGE_LINE, 2))
        gc.StrokePath(path_position)
        
        gc.SetBrush(wx.Brush(COLOR_ORANGE_GLOW))
        gc.SetPen(wx.NullPen)
        for x, y in points_position:
            gc.DrawEllipse(x - 3, y - 3, 6, 6)

        dc.SelectObject(wx.NullBitmap)
        return bitmap

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        w, h = self.GetClientSize()

        if w <= 0 or h <= 0:
            return

        # 1. Regenerasi cache jika belum ada atau terjadi resize
        if self._cached_bitmap is None or self._cached_bitmap.GetSize() != (w, h):
            self._cached_bitmap = self.RebuildChartCache(w, h)

        # 2. Gambar layer statis dari memory (Sangat Cepat!)
        dc.DrawBitmap(self._cached_bitmap, 0, 0, False)

        # 3. Gambar layer dinamis (Hanya Kursor Vertikal & Tooltip Pop-up)
        if 0 <= self.current_time_review <= self.timeline_max:
            gc = wx.GraphicsContext.Create(dc)
            if gc:
                gc.SetAntialiasMode(wx.ANTIALIAS_DEFAULT)
                self.DrawCursorOverlay(dc, gc)

    def DrawCursorOverlay(self, dc, gc):
        cx, cy, cw, ch = self.GetChartCoords()
        axis_font = wx.Font(9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        idx = bisect.bisect_left(self.times, self.current_time_review)
        if idx == 0: idx = 0
        elif idx >= len(self.times): idx = len(self.times) - 1
        else:
            if self.current_time_review - self.times[idx-1] < self.times[idx] - self.current_time_review:
                idx = idx - 1

        review_time = self.times[idx]
        review_pos_val = self.data_position[idx]
        review_hoist_val = self.data_hoist[idx]
        
        x_line, _ = self.WorldToClient(review_time, 0, self.min_y_pos, self.max_y_pos)

        # Dashed vertical line
        gc.SetPen(wx.Pen(wx.Colour(255, 255, 255, 150), 2, wx.PENSTYLE_SHORT_DASH))
        gc.StrokeLine(x_line, cy, x_line, cy + ch)
        
        # Time Badge
        time_str = self.FormatTime(review_time)
        gc.SetFont(axis_font, wx.WHITE)
        tw, th = dc.GetTextExtent(time_str)
        
        path_time_box = gc.CreatePath()
        path_time_box.AddRoundedRectangle(x_line - tw/2 - 10, cy - th - 15, tw + 20, th + 10, 4)
        gc.SetBrush(gc.CreateLinearGradientBrush(x_line, cy-th-15, x_line, cy-5, COLOR_HOVER_POPUP, wx.Colour(0,0,0,230)))
        gc.SetPen(wx.NullPen)
        gc.FillPath(path_time_box)
        gc.DrawText(time_str, x_line - tw/2, cy - th - 10)

        # Detail Tooltip Card
        popup_w, popup_h = 160, 80
        popup_x = x_line + 15
        if popup_x + popup_w > cx + cw:
            popup_x = x_line - popup_w - 15
        popup_y = cy + ch/2 - popup_h/2
        
        gc.SetBrush(wx.Brush(COLOR_HOVER_POPUP))
        gc.SetPen(wx.Pen(wx.Colour(100, 100, 100, 150), 1))
        gc.DrawRoundedRectangle(popup_x, popup_y, popup_w, popup_h, 6)
        
        font_bold = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font_bold, COLOR_ORANGE_GLOW)
        gc.DrawEllipse(popup_x + 10, popup_y + 15, 8, 8)
        gc.DrawText("Position:", popup_x + 30, popup_y + 12)
        
        font_normal = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        gc.SetFont(font_normal, COLOR_ORANGE_GLOW)
        pos_val_str = f"{review_pos_val:.2f} m"
        tw, th = dc.GetTextExtent(pos_val_str)
        gc.DrawText(pos_val_str, popup_x + popup_w - tw - 10, popup_y + 12)

        gc.SetFont(font_bold, COLOR_BLUE)
        gc.SetBrush(wx.Brush(COLOR_BLUE))
        gc.DrawEllipse(popup_x + 10, popup_y + 45, 8, 8)
        gc.DrawText("Hoist:", popup_x + 30, popup_y + 42)
        
        gc.SetFont(font_normal, COLOR_BLUE)
        hoist_val_str = f"{review_hoist_val:.2f} m"
        tw, th = dc.GetTextExtent(hoist_val_str)
        gc.DrawText(hoist_val_str, popup_x + popup_w - tw - 10, popup_y + 42)

    def OnMouseMove(self, event):
        x, y = event.GetPosition()
        cx, cy, cw, ch = self.GetChartCoords()
        if cx <= x <= cx + cw and cy <= y <= cy + ch:
            time_at_mouse = self.ClientToWorldTime(x)
            if self.current_time_review != time_at_mouse:
                self.current_time_review = time_at_mouse
                self.Refresh(False)
        elif self.current_time_review >= 0:
            self.current_time_review = -1
            self.Refresh(False)
        event.Skip()

    def OnMouseLeave(self, event):
        if self.current_time_review >= 0:
            self.current_time_review = -1
            self.Refresh(False)
        event.Skip()

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Helicopter SAR - Control Center", size=(1200, 750))
        self.SetBackgroundColour(COLOR_BG)
        
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left Panel (Summary)
        left_panel = wx.Panel(self)
        left_panel.SetBackgroundColour(wx.Colour(25, 29, 39))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_panel.SetSizer(left_sizer)
        
        summary_title = wx.StaticText(left_panel, label="SESSION SUMMARY")
        summary_title.SetForegroundColour(wx.WHITE)
        summary_title.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        left_sizer.Add(summary_title, 0, wx.ALL, 20)
        
        stats_sizer = wx.FlexGridSizer(rows=6, cols=2, vgap=15, hgap=10)
        stats_sizer.AddGrowableCol(1)
        
        icon_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        value_font = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        def add_stat_row(icon_label, stat_label, val_str, val_color, val_unit):
            icon_text = wx.StaticText(left_panel, label=icon_label)
            icon_text.SetFont(icon_font)
            icon_text.SetForegroundColour(COLOR_TAB_UNSELECTED)
            stats_sizer.Add(icon_text, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 15)

            h_sizer = wx.BoxSizer(wx.HORIZONTAL)
            label_text = wx.StaticText(left_panel, label=stat_label)
            label_text.SetFont(label_font)
            label_text.SetForegroundColour(wx.WHITE)
            h_sizer.Add(label_text, 0, wx.ALIGN_CENTER_VERTICAL)
            
            h_sizer.AddStretchSpacer(1)
            
            value_text = wx.StaticText(left_panel, label=val_str)
            value_text.SetFont(value_font)
            value_text.SetForegroundColour(val_color)
            h_sizer.Add(value_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
            
            unit_text = wx.StaticText(left_panel, label=val_unit)
            unit_text.SetFont(value_font)
            unit_text.SetForegroundColour(val_color)
            h_sizer.Add(unit_text, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 2)
            
            stats_sizer.Add(h_sizer, 0, wx.EXPAND | wx.RIGHT, 15)

        add_stat_row("P", "Max Position", "4.72", COLOR_ORANGE_GLOW, "m")
        add_stat_row("H", "Max Hoist Length", "12.84", COLOR_BLUE, "m")
        add_stat_row("C", "Hoist Cycles", "2", wx.WHITE, "")
        add_stat_row("D", "Total Duration", "00:04:32", wx.WHITE, "")
        add_stat_row("A", "Average Hoist", "6.21", wx.WHITE, "m")
        add_stat_row("N", "Data Points", "5,432", wx.WHITE, "")
        
        left_sizer.Add(stats_sizer, 1, wx.EXPAND | wx.TOP, 10)
        main_sizer.Add(left_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        # Right Panel (Tab & Chart)
        right_panel = wx.Panel(self)
        right_panel.SetBackgroundColour(wx.Colour(25, 29, 39))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_panel.SetSizer(right_sizer)
        
        # Tabs
        tabs = ["Timeline", "Position", "Hoist"]
        self.tab_ctrl = CustomTabControl(right_panel, tabs=tabs, size=(500, 60))
        right_sizer.Add(self.tab_ctrl, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)
        
        # Chart
        self.chart_ctrl = TimelineChartControl(right_panel, timeline_max=300)
        right_sizer.Add(self.chart_ctrl, 1, wx.EXPAND | wx.TOP, 15)
        
        # Bottom Slider
        timeline_slider_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_current_time = wx.StaticText(right_panel, label="00:00")
        self.lbl_current_time.SetForegroundColour(wx.WHITE)
        self.lbl_current_time.SetFont(label_font)
        timeline_slider_sizer.Add(self.lbl_current_time, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
        
        self.slider = wx.Slider(right_panel, value=0, minValue=0, maxValue=300, style=wx.SL_HORIZONTAL)
        self.slider.SetBackgroundColour(COLOR_BG)
        timeline_slider_sizer.Add(self.slider, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        
        lbl_max_time = wx.StaticText(right_panel, label="04:32")
        lbl_max_time.SetForegroundColour(wx.WHITE)
        lbl_max_time.SetFont(label_font)
        timeline_slider_sizer.Add(lbl_max_time, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 20)
        
        right_sizer.Add(timeline_slider_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 15)
        
        main_sizer.Add(right_panel, 3, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(main_sizer)

class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True

if __name__ == "__main__":
    app = App()
    app.MainLoop()