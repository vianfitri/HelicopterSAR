from __future__ import annotations


class DashboardController:

    def __init__(self, dashboard):

        self.dashboard = dashboard

        self.track_position = 5.0
        self.hoist_length = 5.0

        self.update_views()

    # ======================================================
    # Track
    # ======================================================

    def set_track_position(self, value: float):

        self.track_position = value

        self.update_track()

    # ======================================================
    # Hoist
    # ======================================================

    def set_hoist_length(self, value: float):

        self.hoist_length = value

        self.update_hoist()

    # ======================================================
    # Update
    # ======================================================

    def update_track(self):

        self.dashboard.track.set_position(
            self.track_position
        )

        self.dashboard.transversal.display.set_value(
            self.track_position
        )

    def update_hoist(self):

        self.dashboard.hoist.set_value(
            self.hoist_length
        )

        self.dashboard.hoist_control.display.set_value(
            self.hoist_length
        )

    def update_views(self):

        self.update_track()
        self.update_hoist()