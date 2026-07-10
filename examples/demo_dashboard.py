import wx

from ui.dashboard.dashboard import Dashboard


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="AeroSAR Dashboard",
            size=(1280, 720),
        )

        panel = wx.Panel(self)
        panel.SetBackgroundColour(
            wx.Colour(30, 32, 38)
        )

        sizer = wx.BoxSizer(wx.VERTICAL)

        dashboard = Dashboard(panel)
        dashboard.SetFocus()

        sizer.Add(
            dashboard,
            1,
            wx.EXPAND | wx.ALL,
            10,
        )

        panel.SetSizer(sizer)


app = wx.App(False)

frame = DemoFrame()

frame.Show()

app.MainLoop()