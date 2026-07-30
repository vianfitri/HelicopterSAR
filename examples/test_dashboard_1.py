import wx

app = wx.App()

# --- PALET WARNA DARI GAMBAR ---
COLOR_BG = wx.Colour("#0A0E1A")          # Main Background
COLOR_SURFACE = wx.Colour("#121826")     # Card/Panel Background
COLOR_BORDER = wx.Colour("#1E293B")      # Border Lines
COLOR_ACCENT_BLUE = wx.Colour("#00B2FF") # Primary Blue Text / Highlights
COLOR_ACCENT_RED = wx.Colour("#DC2626")  # Stop Button / Critical
COLOR_ACCENT_GREEN = wx.Colour("#10B981")# Status Normal / Connected
COLOR_TEXT_WHITE = wx.Colour("#F8FAFC")
COLOR_TEXT_MUTED = wx.Colour("#64748B")


class ModernCardPanel(wx.Panel):
    """Panel serbaguna dengan sudut melengkung dan background gelap custom."""
    def __init__(self, parent, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER, radius=12):
        super().__init__(parent)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            w, h = self.GetClientSize()
            if w <= 0 or h <= 0:
                return

            path = gc.CreatePath()
            path.AddRoundedRectangle(1, 1, w - 2, h - 2, self.radius)

            gc.SetBrush(gc.CreateBrush(wx.Brush(self.bg_color)))
            gc.SetPen(gc.CreatePen(wx.Pen(self.border_color, 1)))
            gc.DrawPath(path)


class HelicopterDashboard(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Helicopter Simulation Dashboard", size=(1280, 800))
        self.SetMinSize((1024, 720))
        self.SetBackgroundColour(COLOR_BG)

        # Root Sizer
        root_sizer = wx.BoxSizer(wx.VERTICAL)

        # Build UI Sections
        root_sizer.Add(self.build_top_header(), 0, wx.EXPAND | wx.ALL, 12)

        main_body = wx.BoxSizer(wx.HORIZONTAL)
        main_body.Add(self.build_sidebar(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)
        
        # Center & Right Panel Split
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)
        content_sizer.Add(self.build_transversal_panel(), 1, wx.EXPAND | wx.RIGHT, 12)
        content_sizer.Add(self.build_hoist_panel(), 1, wx.EXPAND, 0)
        
        main_body.Add(content_sizer, 1, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 12)
        root_sizer.Add(main_body, 1, wx.EXPAND)

        root_sizer.Add(self.build_bottom_bar(), 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        self.SetSizer(root_sizer)
        self.Center()

    def build_top_header(self):
        """Header Atas: Logo, Title, Status Simulation, dan Action Button."""
        pnl = ModernCardPanel(self, radius=8)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # App Title & Subtitle
        title_box = wx.BoxSizer(wx.VERTICAL)
        t1 = wx.StaticText(pnl, label="HELICOPTER SIMULATION")
        t1.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        t1.SetForegroundColour(COLOR_TEXT_WHITE)
        
        t2 = wx.StaticText(pnl, label="Transversal Position & Hoist Length Monitor")
        t2.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        t2.SetForegroundColour(COLOR_TEXT_MUTED)
        
        title_box.Add(t1, 0, wx.EXPAND)
        title_box.Add(t2, 0, wx.EXPAND)

        # Status Pill Center
        status_btn = wx.Button(pnl, label="● Simulation Running     00:01:23")
        status_btn.SetBackgroundColour(wx.Colour("#132338"))
        status_btn.SetForegroundColour(COLOR_ACCENT_BLUE)

        # Stop Button Right
        stop_btn = wx.Button(pnl, label="█  STOP SIMULATION")
        stop_btn.SetBackgroundColour(COLOR_ACCENT_RED)
        stop_btn.SetForegroundColour(COLOR_TEXT_WHITE)

        sizer.Add(title_box, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        sizer.AddStretchSpacer()
        sizer.Add(status_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        sizer.Add(stop_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        pnl.SetSizer(sizer)
        return pnl

    def build_sidebar(self):
        """Sidebar Kiri: Menu Navigasi, Parameter Info, dan Status Serial Port."""
        pnl = ModernCardPanel(self, radius=10)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Menu List
        menu_items = ["Dashboard", "Scenario", "Parameter", "Data Log", "Chart & Graph", "Export Data", "Settings"]
        for item in menu_items:
            btn = wx.Button(pnl, label=item, size=(-1, 36))
            if item == "Dashboard":
                btn.SetBackgroundColour(wx.Colour("#1D2D44"))
                btn.SetForegroundColour(COLOR_ACCENT_BLUE)
            else:
                btn.SetBackgroundColour(COLOR_SURFACE)
                btn.SetForegroundColour(COLOR_TEXT_MUTED)
            sizer.Add(btn, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 6)

        sizer.AddStretchSpacer()

        # Simulation Info
        info_label = wx.StaticText(pnl, label="SIMULATION INFO")
        info_label.SetForegroundColour(COLOR_TEXT_MUTED)
        info_label.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        sizer.Add(info_label, 0, wx.LEFT | wx.BOTTOM, 12)

        # Connected Card Bottom
        conn_card = ModernCardPanel(pnl, bg_color=wx.Colour("#0F1E2E"), border_color=COLOR_ACCENT_GREEN, radius=8)
        csizer = wx.BoxSizer(wx.VERTICAL)
        lbl_conn = wx.StaticText(conn_card, label="● Connected")
        lbl_conn.SetForegroundColour(COLOR_ACCENT_GREEN)
        lbl_sub = wx.StaticText(conn_card, label="COM5 • 115200 bps")
        lbl_sub.SetForegroundColour(COLOR_TEXT_MUTED)
        csizer.Add(lbl_conn, 0, wx.ALL, 6)
        csizer.Add(lbl_sub, 0, wx.LEFT | wx.BOTTOM, 6)
        conn_card.SetSizer(csizer)

        sizer.Add(conn_card, 0, wx.EXPAND | wx.ALL, 10)

        pnl.SetSizer(sizer)
        pnl.SetMinSize((180, -1))
        return pnl

    def build_transversal_panel(self):
        """Card Utama 1: Transversal Position (Simulasi + Stats)."""
        card = ModernCardPanel(self, radius=12)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Title
        title = wx.StaticText(card, label="1  TRANSVERSAL POSITION")
        title.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(COLOR_TEXT_WHITE)
        sizer.Add(title, 0, wx.ALL, 16)

        # Visualizer Placeholder
        vis_pnl = ModernCardPanel(card, bg_color=wx.Colour("#080B11"), radius=8)
        vis_sizer = wx.BoxSizer(wx.VERTICAL)
        vis_txt = wx.StaticText(vis_pnl, label="[ Area Visualisasi Helikopter - Perspective Track ]")
        vis_txt.SetForegroundColour(COLOR_TEXT_MUTED)
        vis_sizer.Add(vis_txt, 1, wx.ALIGN_CENTER)
        vis_pnl.SetSizer(vis_sizer)
        
        sizer.Add(vis_pnl, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        # Position Reader Box
        pos_card = ModernCardPanel(card, bg_color=wx.Colour("#0F172A"), radius=8)
        psizer = wx.BoxSizer(wx.VERTICAL)
        
        val_lbl = wx.StaticText(pos_card, label="-0.23 m")
        val_lbl.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        val_lbl.SetForegroundColour(COLOR_ACCENT_BLUE)
        
        psizer.Add(val_lbl, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        pos_card.SetSizer(psizer)

        sizer.Add(pos_card, 1, wx.EXPAND | wx.ALL, 16)

        card.SetSizer(sizer)
        return card

    def build_hoist_panel(self):
        """Card Utama 2: Hoist Length (Grafik Vertikal + Manual Controls)."""
        card = ModernCardPanel(self, radius=12)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Header Title
        title = wx.StaticText(card, label="2  HOIST LENGTH")
        title.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        title.SetForegroundColour(COLOR_TEXT_WHITE)
        sizer.Add(title, 0, wx.ALL, 16)

        # Middle Content Placeholder
        hoist_vis = ModernCardPanel(card, bg_color=wx.Colour("#080B11"), radius=8)
        h_sizer = wx.BoxSizer(wx.VERTICAL)
        h_txt = wx.StaticText(hoist_vis, label="[ Model Helikopter & Hoist Length Gauge ]")
        h_txt.SetForegroundColour(COLOR_TEXT_MUTED)
        h_sizer.Add(h_txt, 1, wx.ALIGN_CENTER)
        hoist_vis.SetSizer(h_sizer)

        sizer.Add(hoist_vis, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 16)

        # Control Buttons (RETRACT / STOP / LOWER)
        ctrl_box = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_retract = wx.Button(card, label="↑  RETRACT", size=(-1, 40))
        btn_retract.SetBackgroundColour(wx.Colour("#1E293B"))
        btn_retract.SetForegroundColour(COLOR_ACCENT_BLUE)

        btn_stop = wx.Button(card, label="⏸  STOP", size=(-1, 40))
        btn_stop.SetBackgroundColour(wx.Colour("#3B2514"))
        btn_stop.SetForegroundColour(wx.Colour("#F59E0B"))

        btn_lower = wx.Button(card, label="↓  LOWER", size=(-1, 40))
        btn_lower.SetBackgroundColour(wx.Colour("#1E293B"))
        btn_lower.SetForegroundColour(COLOR_ACCENT_BLUE)

        ctrl_box.Add(btn_retract, 1, wx.RIGHT, 8)
        ctrl_box.Add(btn_stop, 1, wx.RIGHT, 8)
        ctrl_box.Add(btn_lower, 1)

        sizer.Add(ctrl_box, 0, wx.EXPAND | wx.ALL, 16)

        card.SetSizer(sizer)
        return card

    def build_bottom_bar(self):
        """Action Bar di Bawah Dashboard."""
        bar = ModernCardPanel(self, radius=8)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        actions = ["Reset View", "Center Helikopter", "Calibrate", "Record Data", "Take Snapshot", "Export CSV"]
        for act in actions:
            btn = wx.Button(bar, label=act, size=(-1, 36))
            btn.SetBackgroundColour(wx.Colour("#141C2E"))
            btn.SetForegroundColour(COLOR_TEXT_WHITE if "Record" not in act else COLOR_ACCENT_RED)
            sizer.Add(btn, 1, wx.EXPAND | wx.RIGHT if act != actions[-1] else wx.EXPAND, 8)

        bar.SetSizer(sizer)
        return bar


if __name__ == "__main__":
    
    frame = HelicopterDashboard()
    frame.Show()
    app.MainLoop()