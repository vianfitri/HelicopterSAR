from __future__ import annotations


class DashboardState:

    def __init__(self):

        #
        # Transversal
        #

        self.track_position = 5.0
        self.track_minimum = 0.0
        self.track_maximum = 10.0

        #
        # Hoist
        #

        self.hoist_length = 5.0
        self.hoist_minimum = 0.0
        self.hoist_maximum = 10.0

        #
        # Simulator
        #

        self.running = False
        self.paused = False

        #
        # Animation
        #

        self.frame = 0
        self.elapsed = 0.0