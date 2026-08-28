import wx

class SidebarTabControl(wx.Control):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.NO_BORDER):
        super(SidebarTabControl, self).__init__(parent, id, pos, size, style)
        
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        # Data Tab: List of dict (label, icon_normal, icon_active)
        self.tabs = []
        self.selected_index = 1  # Default terpilih (misal: History)
        self.hover_index = -1
        
        self.item_height = 48
        self.padding_left = 16
        
        # Skema Warna
        self.color_bg = wx.Colour(22, 27, 34)              # Background sidebar
        self.color_text_normal = wx.Colour(160, 165, 175)  # Text & Icon redup
        self.color_text_active = wx.Colour(255, 255, 255)  # Text terang
        self.color_orange = wx.Colour(235, 130, 20)        # Warna garis & aksen orange
        
        # Warna Gradasi Tab Aktif (Atas -> Bawah)
        self.grad_start = wx.Colour(120, 55, 10, 180)      # Cokelat orange semi-transparan
        self.grad_end = wx.Colour(70, 30, 5, 100)
        
        # Binding Event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

    def AddTab(self, label, bitmap_normal=None, bitmap_active=None):
        """Menambahkan tab baru ke sidebar."""
        self.tabs.append({
            'label': label,
            'bmp_normal': bitmap_normal,
            'bmp_active': bitmap_active
        })
        self.Refresh()

    def SetSelection(self, index):
        """Mengubah tab terpilih berdasarkan indeks."""
        if 0 <= index < len(self.tabs) and index != self.selected_index:
            self.selected_index = index
            self.Refresh()
            
            # Post event perubah tab
            evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            evt.SetInt(index)
            evt.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(evt)

    def GetSelection(self):
        return self.selected_index

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.color_bg))
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        width, height = self.GetClientSize()
        
        # Font setup
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, self.color_text_normal)

        for i, tab in enumerate(self.tabs):
            y = i * self.item_height
            rect = wx.Rect(0, y, width, self.item_height)
            is_selected = (i == self.selected_index)

            # Draw Selected Tab Background & Accent
            if is_selected:
                # 1. Background Gradient Tab Aktif
                brush = gc.CreateLinearGradientBrush(
                    0, y, 0, y + self.item_height, 
                    self.grad_start, self.grad_end
                )
                gc.SetBrush(brush)
                gc.SetPen(wx.NullPen)
                gc.DrawRoundedRectangle(4, y + 2, width - 8, self.item_height - 4, 4)

                # 2. Garis Vertikal Orange di Kiri
                gc.SetBrush(gc.CreateBrush(wx.Brush(self.color_orange)))
                gc.DrawRoundedRectangle(0, y + 4, 4, self.item_height - 8, 2)

            # Draw Bitmap / Icon (jika ada)
            bmp = tab['bmp_active'] if is_selected else tab['bmp_normal']
            x_offset = self.padding_left + 8
            
            if bmp and bmp.IsOk():
                gc.DrawBitmap(bmp, x_offset, y + (self.item_height - bmp.GetHeight()) // 2, bmp.GetWidth(), bmp.GetHeight())
                x_offset += bmp.GetWidth() + 12
            else:
                x_offset += 24  # Placeholder spasi jika tidak ada gambar

            # Draw Label Text
            text_color = self.color_orange if is_selected else self.color_text_normal
            gc.SetFont(font, text_color)
            
            # Vertically center text
            _, txt_h = dc.GetTextExtent(tab['label'])
            gc.DrawText(tab['label'], x_offset, y + (self.item_height - txt_h) / 2)

    def OnLeftDown(self, event):
        y = event.GetY()
        clicked_index = y // self.item_height
        if 0 <= clicked_index < len(self.tabs):
            self.SetSelection(clicked_index)

    def OnMouseMotion(self, event):
        y = event.GetY()
        hover_index = y // self.item_height
        if 0 <= hover_index < len(self.tabs):
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        else:
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def OnMouseLeave(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def OnSize(self, event):
        self.Refresh()
        event.Skip()


# --- CONTOH PENGGUNAAN / TEST FRAME ---
class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(None, title="Sidebar TabControl Demo", size=(800, 500))
        self.SetBackgroundColour(wx.Colour(18, 22, 28))

        # Main Layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Custom Sidebar Control
        self.sidebar = SidebarTabControl(self, size=(200, -1))
        
        # Menambahkan Tab
        self.sidebar.AddTab("Training")
        self.sidebar.AddTab("History")
        self.sidebar.AddTab("Sessions")
        self.sidebar.AddTab("Settings")
        self.sidebar.AddTab("About")

        # Event ketika tab diganti
        self.sidebar.Bind(wx.EVT_BUTTON, self.OnTabChanged)

        # Panel Konten Kanan (Placeholder)
        self.content_panel = wx.Panel(self)
        self.content_panel.SetBackgroundColour(wx.Colour(28, 33, 40))
        
        self.label_title = wx.StaticText(self.content_panel, label="SESSION DETAIL #014", pos=(20, 20))
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label_title.SetFont(font)
        self.label_title.SetForegroundColour(wx.Colour(255, 255, 255))

        # Susun Layout
        main_sizer.Add(self.sidebar, 0, wx.EXPAND | wx.ALL, 0)
        main_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        self.SetSizer(main_sizer)

    def OnTabChanged(self, event):
        selected_idx = event.GetInt()
        tab_name = self.sidebar.tabs[selected_idx]['label']
        self.label_title.SetLabel(f"Halaman: {tab_name.upper()}")

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()