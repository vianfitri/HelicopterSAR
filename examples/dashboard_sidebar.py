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

        body.Add(sidebar, 0, wx.EXPAND)
        body.Add(content, 1, wx.EXPAND | wx.ALL, 15)

        root.Add(body, 1, wx.EXPAND)

        panel.SetSizer(root)


# ==========================
# Main
# ==========================
if __name__ == "__main__":
    app = wx.App()
    frame = Dashboard()
    frame.Center()
    frame.Show()
    app.MainLoop()