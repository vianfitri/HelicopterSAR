"""
Demo ModernCard
"""

import wx

from ui.panels.modern_card import ModernCard
from ui.controls.labels import Label


class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="ModernCard Demo",
            size=(1000, 600),
        )

        panel = wx.Panel(self)

        panel.SetBackgroundColour(wx.Colour(30, 30, 30))

        layout = wx.BoxSizer(wx.HORIZONTAL)

        position = ModernCard(
            panel,
            title="TRANSVERSAL POSITION",
        )

        hoist = ModernCard(
            panel,
            title="HOIST LENGTH",
        )

        position.body_sizer.AddStretchSpacer()

        position.body_sizer.Add(
            Label.display(
                position.body_panel,
                "+2.35",
            ),
            0,
            wx.ALIGN_CENTER,
        )

        position.body_sizer.Add(
            Label.caption(
                position.body_panel,
                "meter",
            ),
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            20,
        )

        position.body_sizer.AddStretchSpacer()

        hoist.body_sizer.AddStretchSpacer()

        hoist.body_sizer.Add(
            Label.display(
                hoist.body_panel,
                "8.42",
            ),
            0,
            wx.ALIGN_CENTER,
        )

        hoist.body_sizer.Add(
            Label.caption(
                hoist.body_panel,
                "meter",
            ),
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            20,
        )

        hoist.body_sizer.AddStretchSpacer()

        layout.Add(
            position,
            1,
            wx.EXPAND | wx.ALL,
            20,
        )

        layout.Add(
            hoist,
            1,
            wx.EXPAND | wx.ALL,
            20,
        )

        panel.SetSizer(layout)


app = wx.App(False)
frame = DemoFrame()
frame.Show()

app.MainLoop()