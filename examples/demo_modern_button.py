"""
Helicopter SAR Simulator
examples/demo_modern_button.py

Demo ModernButton.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

import wx

from ui.controls.modern_button import ModernButton


# ==========================================================
# Demo Frame
# ==========================================================

class DemoFrame(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="ModernButton Demo",
            size=(700, 450),
        )

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(30, 30, 30))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_connect = ModernButton(
            panel,
            label="CONNECT",
        )

        self.btn_start = ModernButton(
            panel,
            label="START",
        )

        self.btn_stop = ModernButton(
            panel,
            label="STOP",
        )

        self.btn_reset = ModernButton(
            panel,
            label="RESET",
        )

        self.btn_emergency = ModernButton(
            panel,
            label="EMERGENCY",
        )

        self.btn_disabled = ModernButton(
            panel,
            label="DISABLED",
        )
        self.btn_disabled.Enable(False)

        buttons = (
            self.btn_connect,
            self.btn_start,
            self.btn_stop,
            self.btn_reset,
            self.btn_emergency,
            self.btn_disabled,
        )

        for button in buttons:

            button.Bind(
                wx.EVT_BUTTON,
                self.on_button_clicked,
            )

            button_sizer.Add(
                button,
                0,
                wx.ALL,
                8,
            )

        main_sizer.AddStretchSpacer()

        main_sizer.Add(
            button_sizer,
            0,
            wx.ALIGN_CENTER,
        )

        main_sizer.AddStretchSpacer()
        panel.SetSizer(main_sizer)
        self.Centre()

    # ------------------------------------------------------

    def on_button_clicked(self, event):

        button = event.GetEventObject()
        print(f"{button.label} clicked")


# ==========================================================
# Main
# ==========================================================

def main():

    app = wx.App(False)
    frame = DemoFrame()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()