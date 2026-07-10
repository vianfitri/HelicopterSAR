import wx

from ui.controls.modern_slider import ModernSlider
from ui.widgets.hoist_view import HoistView


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="HoistView Demo",
            size=(300, 650),
        )

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 32, 38))

        root = wx.BoxSizer(wx.VERTICAL)

        self.view = HoistView(
            panel,
            minimum=0,
            maximum=10,
            value=5,
            size=(180, 450),
        )

        self.slider = ModernSlider(
            panel,
            minimum=0,
            maximum=10,
            value=5,
            orientation=wx.HORIZONTAL,
            size=(220, 40),
        )

        self.slider.Bind(
            wx.EVT_SLIDER,
            self.on_slider,
        )

        root.Add(
            self.view,
            1,
            wx.ALIGN_CENTER | wx.ALL,
            20,
        )

        root.Add(
            self.slider,
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            20,
        )

        panel.SetSizer(root)

    def on_slider(self, event):

        self.view.set_value(
            self.slider.value
        )


app = wx.App(False)

frame = DemoFrame()

frame.Show()

app.MainLoop()