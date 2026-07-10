from __future__ import annotations

import wx

from ui.base.base_panel import BasePanel

from ui.widgets.track_view import TrackView
from ui.widgets.hoist_view import HoistView
from ui.widgets.helicopter_view import HelicopterView
from ui.widgets.sea_view import SeaView

from ui.panels.control_panel import ControlPanel
from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_keyboard import DashboardKeyboard
#from ui.dashboard.dashboard_timer import DashboardTimer
from ui.dashboard.dashboard_repeat import DashboardRepeat

class Dashboard(BasePanel):

    def __init__(
        self,
        parent: wx.Window,
        **kwargs,
    ):

        super().__init__(
            parent,
            **kwargs,
        )

    # ------------------------------------------------------

    def initialize(self):

        root = wx.BoxSizer(wx.HORIZONTAL)

        # ==================================================
        # LEFT
        # ==================================================

        left = wx.BoxSizer(wx.VERTICAL)

        #self.track = TrackView(
        #    self,
        #    minimum=0,
        #    maximum=10,
        #    value=5,
        #    size=(760, 160),
        #)
        self.track = HelicopterView(
            self,
            size=(760, 240),
        )

        self.transversal = ControlPanel(
            self,
            title="TRANSVERSAL POSITION",
        )

        self.sea = SeaView(
            self,
            size=(760, 220),
        )

        left.Add(
            self.track,
            0,
            wx.EXPAND | wx.ALL,
            10,
        )

        left.Add(
            self.sea,
            1,
            wx.EXPAND | wx.LEFT | wx.RIGHT,
            10,
        )

        left.Add(
            self.transversal,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10,
        )

        # ==================================================
        # RIGHT
        # ==================================================

        right = wx.BoxSizer(wx.VERTICAL)

        self.hoist = HoistView(
            self,
            minimum=0,
            maximum=10,
            value=5,
            size=(220, 520),
        )

        self.hoist_control = ControlPanel(
            self,
            title="HOIST LENGTH",
        )

        right.Add(
            self.hoist,
            1,
            wx.EXPAND | wx.ALL,
            10,
        )

        right.Add(
            self.hoist_control,
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            10,
        )

        # ==================================================

        root.Add(
            left,
            1,
            wx.EXPAND,
        )

        root.Add(
            right,
            0,
            wx.EXPAND,
        )

        self.SetSizer(root)

        # ==================================================
        # Events
        # ==================================================

        self.transversal.slider.Bind(
            wx.EVT_SLIDER,
            self.on_track_slider,
        )

        self.hoist_control.slider.Bind(
            wx.EVT_SLIDER,
            self.on_hoist_slider,
        )

        self.transversal.btn_minus.Bind(wx.EVT_LEFT_DOWN, self.on_track_minus_down)
        self.transversal.btn_minus.Bind(wx.EVT_LEFT_UP, self.on_repeat_stop)
        self.transversal.btn_plus.Bind(wx.EVT_LEFT_DOWN, self.on_track_plus_down)
        self.transversal.btn_plus.Bind(wx.EVT_LEFT_UP, self.on_repeat_stop)

        self.hoist_control.btn_minus.Bind(wx.EVT_LEFT_DOWN, self.on_hoist_minus_down)
        self.hoist_control.btn_minus.Bind(wx.EVT_LEFT_UP, self.on_repeat_stop)
        self.hoist_control.btn_plus.Bind(wx.EVT_LEFT_DOWN, self.on_hoist_plus_down)
        self.hoist_control.btn_plus.Bind(wx.EVT_LEFT_UP, self.on_repeat_stop)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        # ==================================================
        # Dashboard Timer
        # ==================================================

        self.timer = wx.Timer(self)

        self.Bind(
            wx.EVT_TIMER,
            self.on_timer,
            self.timer,
        )

        self.timer.Start(50)

        # ==================================================
        # Controller
        # ==================================================

        self.controller = DashboardController(self)

        self.keyboard = DashboardKeyboard(self)

        #self.timer = DashboardTimer(self)

        self.repeat = DashboardRepeat(self)

    # ------------------------------------------------------

    def on_track_slider(self, event):

        value = self.transversal.slider.value

        self.controller.set_track_position(value)

        #self.track.set_position(value)

        #self.transversal.display.set_value(value)

    # ------------------------------------------------------

    def on_hoist_slider(self, event):

        value = self.hoist_control.slider.value

        self.controller.set_hoist_length(value)

        #self.hoist.set_value(value)

        #self.hoist_control.display.set_value(value)

    # ------------------------------------------------------

    def on_track_minus_down(self, event):
        
        self.repeat.start(self.transversal.decrease)
        event.Skip()
    
    def on_track_plus_down(self, event):

        self.repeat.start(self.transversal.increase)
        event.Skip()
    
    def on_hoist_minus_down(self, event):

        self.repeat.start(self.hoist_control.decrease)
        event.Skip()

    def on_hoist_plus_down(self, event):

        self.repeat.start(self.hoist_control.increase)
        event.Skip()

    def on_repeat_stop(self, event):

        self.repeat.stop()
        event.Skip()

    def on_close(self, event):
         
        if self.timer.IsRunning():
             self.timer.Stop()

        self.repeat.stop()
        
        event.Skip()
    
    def on_timer(self, event):

        #state = self.controller.state

        #state.frame += 1
        #state.elapsed += 1.0 / 60.0

        #self.sea.set_phase(state.elapsed * 2.5)
        pass

    def update(self):

        #
        # Refresh custom widget
        #

        self.track.Refresh(False)
        self.hoist.Refresh(False)
        self.transversal.Refresh(False)
        self.hoist_control.Refresh(False)