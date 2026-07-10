"""
AeroSAR Simulator
ui/controls/modern_slider.py
"""

from __future__ import annotations
import wx
from ui.base.base_widget import BaseWidget

class ModernSlider(BaseWidget):
    """
    Modern custom slider.

    Features
    --------
    - Horizontal / Vertical
    - Float value
    - Custom painting
    - Mouse dragging
    - wx.CommandEvent notification
    """

    #TRACK_THICKNESS = 6
    #THUMB_RADIUS = 9
    #MARGIN = 14

    TRACK_THICKNESS = 5

    THUMB_RADIUS = 8
    THUMB_RADIUS_HOVER = 10
    THUMB_RADIUS_DRAG = 11

    MARGIN = 16

    BORDER_WIDTH = 2


    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        minimum: float = 0.0,
        maximum: float = 100.0,
        value: float = 0.0,
        orientation: int = wx.HORIZONTAL,
        **kwargs,
    ):

        self._minimum = minimum
        self._maximum = maximum
        self._value = value

        self._orientation = orientation

        self._hover = False
        self._dragging = False

        super().__init__(
            parent,
            id=id,
            **kwargs,
        )

        self.initialize()
        self.bind_events()

    # ==================================================
    # Initialization
    # ==================================================

    def initialize(self):
        if self._orientation == wx.HORIZONTAL:
            self.SetMinSize(
                (
                    self.dip(220),
                    self.dip(40),
                )
            )
        
        else:
            self.SetMinSize(
                (
                    self.dip(40),
                    self.dip(220),
                )
            )
         
        self.SetCursor(
            wx.Cursor(wx.CURSOR_HAND)
        )

    # ==================================================
    # Event Binding
    # ==================================================

    def bind_events(self):

        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)

        self.Bind(wx.EVT_MOTION, self._on_motion)

        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)

    # ==================================================
    # Properties
    # ==================================================

    @property
    def value(self):
        return self._value

    @property
    def minimum(self):
        return self._minimum

    @property
    def maximum(self):
        return self._maximum

    # ==================================================
    # Public API
    # ==================================================

    def set_value(self, value: float):

        value = max(
            self._minimum,
            min(
                self._maximum,
                value,
            ),
        )

        if value == self._value:
            return

        self._value = value

        self.Refresh()

        evt = wx.CommandEvent(
            wx.EVT_SLIDER.typeId,
            self.GetId(),
        )

        evt.SetEventObject(self)
        self.ProcessWindowEvent(evt)

    # ==================================================
    # Value Conversion
    # ==================================================

    def _normalized(self):

        span = self._maximum - self._minimum

        if span <= 0:
            return 0.0

        return (
            self._value - self._minimum
        ) / span

    def _track_rect(self):

        w, h = self.GetClientSize()
        m = self.dip(self.MARGIN)

        if self._orientation == wx.HORIZONTAL:

            return (
                m,
                h // 2,
                w - (m * 2),
            )

        return (
            w // 2,
            m,
            h - (m * 2),
        )

    def _thumb_position(self):

        n = self._normalized()

        if self._orientation == wx.HORIZONTAL:
            x, y, length = self._track_rect()

            return (
                x + (length * n),
                y,
            )

        x, y, length = self._track_rect()

        return (
            x,
            y + length - (length * n),
        )
    
        # ==================================================
    # Mouse Events
    # ==================================================

    def _on_enter(self, event):

        self._hover = True
        self.Refresh()

        event.Skip()

    # --------------------------------------------------

    def _on_leave(self, event):

        self._hover = False

        if not self._dragging:
            self.Refresh()

        event.Skip()

    # --------------------------------------------------

    def _on_left_down(self, event):

        self._dragging = True

        if not self.HasCapture():
            self.CaptureMouse()

        self._update_from_mouse(
            event.GetPosition()
        )

        event.Skip()

    # --------------------------------------------------

    def _on_left_up(self, event):

        if self.HasCapture():
            self.ReleaseMouse()

        self._dragging = False

        self.Refresh()

        event.Skip()

    # --------------------------------------------------

    def _on_motion(self, event):

        if self._dragging:

            self._update_from_mouse(
                event.GetPosition()
            )

        event.Skip()

    # ==================================================
    # Mouse -> Value
    # ==================================================

    def _update_from_mouse(
        self,
        pos: wx.Point,
    ):

        if self._orientation == wx.HORIZONTAL:

            x, y, length = self._track_rect()

            ratio = (pos.x - x) / length

        else:

            x, y, length = self._track_rect()

            ratio = 1.0 - ((pos.y - y) / length)

        ratio = max(
            0.0,
            min(
                1.0,
                ratio,
            )
        )

        value = (
            self._minimum +
            ratio *
            (self._maximum - self._minimum)
        )

        self.set_value(value)

    # ==================================================
    # Drawing
    # ==================================================

    def draw(self, gc: wx.GraphicsContext):

        palette = self.palette

        gc.SetAntialiasMode(
            wx.ANTIALIAS_DEFAULT
        )

        if self._orientation == wx.HORIZONTAL:

            self._draw_horizontal(gc)

        else:

            self._draw_vertical(gc)

    # --------------------------------------------------

    def _draw_horizontal(
        self,
        gc: wx.GraphicsContext,
    ):

        palette = self.palette

        x, y, length = self._track_rect()

        track_h = self.dip(
            self.TRACK_THICKNESS
        )

        radius = track_h / 2

        #
        # Track Background
        #

        gc.SetBrush(
            wx.Brush(
                #palette.panel_alt
                palette.separator
            )
        )

        gc.SetPen(
            wx.TRANSPARENT_PEN
        )

        gc.DrawRoundedRectangle(
            x,
            y - track_h / 2,
            length,
            track_h,
            radius,
        )

        #
        # Filled Track
        #

        thumb_x, thumb_y = self._thumb_position()

        gc.SetBrush(
            wx.Brush(
                palette.primary
            )
        )

        gc.DrawRoundedRectangle(
            x,
            y - track_h / 2,
            thumb_x - x,
            track_h,
            radius,
        )

        thumb_r = self.dip(
            self.THUMB_RADIUS
        )

        if self._dragging:
            thumb_r = self.dip(self.THUMB_RADIUS_DRAG)
            #colour = palette.primary_pressed

        elif self._hover:
            thumb_r = self.dip(self.THUMB_RADIUS_HOVER)
            #colour = palette.primary_hover

        #else:

            #colour = palette.primary
        
        #
        # Shadow
        #

        gc.SetBrush(
            wx.Brush(palette.shadow)
        )

        gc.SetPen(
            wx.Pen(
                #palette.border,
                #1,
                wx.TRANSPARENT_PEN
            )
        )

        gc.DrawEllipse(
            thumb_x - thumb_r + 1,
            thumb_y - thumb_r + 2,
            thumb_r * 2,
            thumb_r * 2,
        )

        #
        # Thumb
        #

        gc.SetBrush(wx.Brush(wx.WHITE))

        gc.SetPen(
            wx.Pen(
                palette.primary,
                self.BORDER_WIDTH,
            )
        )

        gc.DrawEllipse(
            thumb_x - thumb_r,
            thumb_y - thumb_r,
            thumb_r * 2,
            thumb_r * 2,
        )

    # --------------------------------------------------

    def _draw_vertical(
        self,
        gc: wx.GraphicsContext,
    ):

        palette = self.palette

        x, y, length = self._track_rect()

        track_w = self.dip(
            self.TRACK_THICKNESS
        )

        radius = track_w / 2

        #
        # Track
        #

        gc.SetBrush(
            wx.Brush(
                #palette.panel_alt
                palette.separator
            )
        )

        gc.SetPen(
            wx.TRANSPARENT_PEN
        )

        gc.DrawRoundedRectangle(
            x - track_w / 2,
            y,
            track_w,
            length,
            radius,
        )

        thumb_x, thumb_y = self._thumb_position()

        #
        # Filled Track
        #

        gc.SetBrush(
            wx.Brush(
                palette.primary
            )
        )

        gc.DrawRoundedRectangle(
            x - track_w / 2,
            thumb_y,
            track_w,
            (y + length) - thumb_y,
            radius,
        )

        thumb_r = self.dip(
            self.THUMB_RADIUS
        )

        if self._dragging:
            thumb_r = self.dip(self.THUMB_RADIUS_DRAG)
            #colour = palette.primary_pressed

        elif self._hover:
            thumb_r = self.dip(self.THUMB_RADIUS_HOVER)
            #colour = palette.primary_hover

        #else:

            #colour = palette.primary
        
        #
        # Shadow
        #

        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.SetBrush(wx.Brush(palette.shadow))

        gc.DrawEllipse(
            thumb_x - thumb_r + 1,
            thumb_y - thumb_r + 2,
            thumb_r * 2,
            thumb_r * 2,
        )

        #
        # Thumb
        #

        gc.SetBrush(wx.Brush(wx.WHITE))

        gc.SetPen(
            wx.Pen(
                #palette.border,
                #1,
                palette.primary,
                self.BORDER_WIDTH,
            )
        )

        gc.DrawEllipse(
            thumb_x - thumb_r,
            thumb_y - thumb_r,
            thumb_r * 2,
            thumb_r * 2,
        )