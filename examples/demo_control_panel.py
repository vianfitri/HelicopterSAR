import wx

from ui.panels.control_panel import ControlPanel


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="Control Panel",
            size=(420, 340),
        )

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 32, 38))

        sizer = wx.BoxSizer(wx.VERTICAL)

        cp = ControlPanel(
            panel,
            title="TRANSVERSAL POSITION",
        )

        sizer.Add(
            cp,
            1,
            wx.EXPAND | wx.ALL,
            20,
        )

        panel.SetSizer(sizer)


app = wx.App(False)

frame = DemoFrame()

frame.Show()

app.MainLoop()