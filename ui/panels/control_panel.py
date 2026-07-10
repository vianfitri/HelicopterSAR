from __future__ import annotations

import wx

from ui.base.base_panel import BasePanel

from ui.controls.numeric_display import NumericDisplay
from ui.controls.modern_slider import ModernSlider
from ui.controls.modern_button import ModernButton


class ControlPanel(BasePanel):

    def __init__(
        self,
        parent,
        title="",
        **kwargs,
    ):

        self._title = title

        super().__init__(
            parent,
            **kwargs,
        )

        #self.initialize()

    # --------------------------------------------------

    def initialize(self):

        root = wx.BoxSizer(wx.VERTICAL)

        #
        # Numeric Display
        #

        self.display = NumericDisplay(
            self,
            title=self._title,
            value=5.00,
            unit="meter",
            size=(260, 140),
        )

        root.Add(
            self.display,
            0,
            wx.EXPAND | wx.ALL,
            10,
        )

        #
        # Slider
        #

        self.slider = ModernSlider(
            self,
            minimum=0,
            maximum=10,
            value=5,
            orientation=wx.HORIZONTAL,
            size=(260, 40),
        )

        root.Add(
            self.slider,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10,
        )

        #
        # Buttons
        #

        btns = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_minus = ModernButton(
            self,
            label="-",
            size=(40, 40),
        )

        self.btn_plus = ModernButton(
            self,
            label="+",
            size=(40, 40),
        )

        btns.Add(
            self.btn_minus,
            0,
            wx.RIGHT,
            8,
        )

        btns.Add(
            self.btn_plus,
            0,
        )

        btns.AddStretchSpacer()

        root.Add(
            btns,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10,
        )

        self.SetSizer(root)

        #
        # Events
        #

        self.slider.Bind(
            wx.EVT_SLIDER,
            self._on_slider,
        )

        self.btn_minus.Bind(
            wx.EVT_BUTTON,
            self._on_minus,
        )

        self.btn_plus.Bind(
            wx.EVT_BUTTON,
            self._on_plus,
        )

        self.SetSizer(root)
        root.SetSizeHints(self)
        self.Layout()

    # --------------------------------------------------

    def _on_slider(self, event):

        self.display.set_value(
            self.slider.value
        )
        #print(self.slider.value)

    # --------------------------------------------------

    def _on_minus(self, event):

        self.decrease()

        #self.slider.set_value(
        #    self.slider.value - 0.1
        #)

        #self.display.set_value(
        #    self.slider.value
        #)

    # --------------------------------------------------

    def _on_plus(self, event):

        self.increase()

        #self.slider.set_value(
        #    self.slider.value + 0.1
        #)

        #self.display.set_value(
        #    self.slider.value
        #)

    # --------------------------------------------------

    def increase(self):

        self.slider.set_value(
            self.slider.value + 0.1
        )

        self.display.set_value(
            self.slider.value
        )

    # --------------------------------------------------

    def decrease(self):

        self.slider.set_value(
            self.slider.value - 0.1
        )

        self.display.set_value(
            self.slider.value
        )

    