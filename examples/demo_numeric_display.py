import wx

from ui.controls.numeric_display import NumericDisplay


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="Numeric Display Demo",
            size=(700, 350),
        )

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 32, 38))

        self.display1 = NumericDisplay(
            panel,
            title="TRANSVERSAL POSITION",
            value=5.24,
            unit="meter",
            pos=(40, 40),
            size=(260, 150),
        )

        self.display2 = NumericDisplay(
            panel,
            title="HOIST LENGTH",
            value=8.72,
            unit="meter",
            pos=(340, 40),
            size=(260, 150),
        )

        self.timer = wx.Timer(self)

        self.Bind(
            wx.EVT_TIMER,
            self.on_timer,
            self.timer,
        )

        self.timer.Start(100)

        self.t = 0.0

    def on_timer(self, event):

        self.t += 0.05

        self.display1.set_value(self.t)

        self.display2.set_value(
            10.0 - self.t
        )


app = wx.App(False)

frame = DemoFrame()

frame.Show()

app.MainLoop()