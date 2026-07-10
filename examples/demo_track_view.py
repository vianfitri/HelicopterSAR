import wx

from ui.controls.modern_slider import ModernSlider
from ui.widgets.track_view import TrackView


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="TrackView Demo",
            size=(900, 300),
        )

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 32, 38))

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.track = TrackView(
            panel,
            minimum=0,
            maximum=10,
            value=5,
            size=(800, 140),
        )

        self.slider = ModernSlider(
            panel,
            minimum=0,
            maximum=10,
            value=5,
            orientation=wx.HORIZONTAL,
            size=(700, 40),
        )

        self.slider.Bind(
            wx.EVT_SLIDER,
            self.on_slider,
        )

        sizer.Add(
            self.track,
            0,
            wx.EXPAND | wx.ALL,
            20,
        )

        sizer.Add(
            self.slider,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            20,
        )

        panel.SetSizer(sizer)

    def on_slider(self, event):

        self.track.set_position(
            self.slider.value
        )


app = wx.App(False)

frame = DemoFrame()
frame.Show()

app.MainLoop()