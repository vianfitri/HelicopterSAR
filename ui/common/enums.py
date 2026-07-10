"""
Helicopter SAR Simulator
ui/common/enums.py

Common UI Enumerations.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

from enum import Enum, auto


# ==========================================================
# Theme
# ==========================================================

class ThemeMode(Enum):
    DARK = auto()
    LIGHT = auto()


# ==========================================================
# Card
# ==========================================================

class CardState(Enum):
    NORMAL = auto()
    ACTIVE = auto()
    WARNING = auto()
    ERROR = auto()
    DISABLED = auto()


# ==========================================================
# Button
# ==========================================================

class ButtonState(Enum):
    NORMAL = auto()
    HOVER = auto()
    PRESSED = auto()
    DISABLED = auto()


# ==========================================================
# Connection
# ==========================================================

class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()


# ==========================================================
# Simulation
# ==========================================================

class SimulationState(Enum):
    STOPPED = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


# ==========================================================
# Mission
# ==========================================================

class MissionState(Enum):
    IDLE = auto()
    SEARCH = auto()
    HOVER = auto()
    RESCUE = auto()
    RETURN = auto()


# ==========================================================
# Hoist
# ==========================================================

class HoistState(Enum):
    STOPPED = auto()
    LOWERING = auto()
    LIFTING = auto()
    HOLD = auto()
    EMERGENCY = auto()


# ==========================================================
# LED
# ==========================================================

class LEDState(Enum):
    OFF = auto()
    ON = auto()
    BLINK = auto()