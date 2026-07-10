from __future__ import annotations

from ui.dashboard.dashboard_state import DashboardState

class DashboardController:

    def __init__(self, dashboard):

        self.dashboard = dashboard
        self.state = DashboardState()

        self.track_position = 5.0
        self.hoist_length = 5.0

        self.update_views()

    # ======================================================
    # Track
    # ======================================================

    def set_track_position(self, value: float):

        value = max(self.state.track_minimum, min(self.state.track_maximum, value))

        self.state.track_position = value

        self.update_track()

    # ======================================================
    # Hoist
    # ======================================================

    def set_hoist_length(self, value: float):

        value = max(self.state.hoist_minimum, min(self.state.hoist_maximum, value))

        self.state.hoist_length = value

        self.update_hoist()

    # ======================================================
    # Update
    # ======================================================

    def update_track(self):

        #self.dashboard.track.set_position(
        #    self.state.track_position
        #)

        self.dashboard.transversal.display.set_value(
            self.state.track_position
        )

        self.dashboard.transversal.slider.set_value(
            self.state.track_position
        )

        self.dashboard.track.set_track_position(
            self.state.track_position
        )

    def update_hoist(self):

        self.dashboard.hoist.set_value(
            self.state.hoist_length
        )

        self.dashboard.hoist_control.display.set_value(
            self.state.hoist_length
        )

        self.dashboard.hoist_control.slider.set_value(
            self.state.hoist_length
        )

        self.dashboard.track.set_hoist_length(
            self.state.hoist_length
        )

    def update_views(self):

        self.update_track()
        self.update_hoist()