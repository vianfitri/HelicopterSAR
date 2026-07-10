import wx

from ui.controls.modern_slider import ModernSlider


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="Modern Slider Demo",
            size=(700, 400),
        )

        panel = wx.Panel(self)

        panel.SetBackgroundColour(wx.Colour(30, 32, 38))

        h = ModernSlider(
            panel,
            minimum=0,
            maximum=10,
            value=5,
            orientation=wx.HORIZONTAL,
            pos=(40, 60),
            size=(220, 40),
        )

        v = ModernSlider(
            panel,
            minimum=0,
            maximum=10,
            value=5,
            orientation=wx.VERTICAL,
            pos=(500, 60),
            size=(40, 220)
        )

        h.Bind(wx.EVT_SLIDER, self.on_slider)
        v.Bind(wx.EVT_SLIDER, self.on_slider)

    def on_slider(self, event):

        slider = event.GetEventObject()

        print(slider.value)


app = wx.App(False)

frame = DemoFrame()

frame.Show()

app.MainLoop()