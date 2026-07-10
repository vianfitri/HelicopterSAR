"""
Helicopter SAR Simulator
Configuration File

Author : Mas Vi & ChatGPT
Version: 0.1.0
"""

from dataclasses import dataclass

# ========================================
# Application Information
# ========================================

APP_NAME = "HelicopterSAR Simulator"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = (
    "Search And Rescue Helicopter Training Simulator"
)

# ========================================
# Window Configuration
# ========================================

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

MIN_WINDOW_WIDTH = 1280
MIN_WINDOW_HEIGHT = 720

FPS = 60

# ========================================
# Layout
# ========================================

HEADER_HEIGHT = 60
TOOLBAR_HEIGHT = 54
STATUSBAR_HEIGHT = 28
SIDEBAR_WIDTH = 220
CONTENT_PADDING = 10
CARD_SPACING = 10

# ========================================
# Simulator
# ========================================

TRACK_LENGTH_METER = 10.0
TRACK_HALF_LENGTH = TRACK_LENGTH_METER / 2
MAX_HOIST_LENGTH = 20.0
MIN_HOIST_LENGTH = 0.0

# ========================================
# Telemetry Refresh Rate
# ========================================

UI_REFRESH_MS = 16      # ~60 FPS
SERIAL_REFRESH_MS = 20  # 50 Hz
GRAPH_REFRESH_MS = 50   # 20 Hz
LOGGER_REFRESH_MS = 100 # 10 Hz

# ========================================
# Animation
# ========================================

ANIMATION_DURATION_MS = 180
ENABLE_ANIMATION = True

# ========================================
# Default Simulator Values
# ========================================

DEFAULT_POSITION = 0.0
DEFAULT_SPEED = 0.0
DEFAULT_HOIST_LENGTH = 0.0
DEFAULT_LOAD = 0.0
DEFAULT_WIND_SPEED = 0.0
DEFAULT_WIND_DIRECTION = 0.0

# ========================================
# Logging
# ========================================

ENABL_DEBUG = True
LOG_DIRECTORY = "logs"
DATA_DIRECTORY = "data"
SCENARIO_DIRECTORY = "scenario"
ASSET_DIRECTORY = "assets"

# ========================================
# Serial Communication
# ========================================

DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 0.05

# ========================================
# Audio
# ========================================

MASTER_VOLUME = 100
HELICOPTER_VOLUME = 100
RAIN_VOLUME = 100
WAVE_VOLUME = 100
WIND_VOLUME = 100

# ========================================
# Theme
# ========================================

DEFAULT_THEME = "dark"

# ========================================
# Runtime State
# ========================================

@dataclass(slots=True)
class RuntimeConfig:
    """
    Konfigurasi yang dapat berubah saat aplikasi berjalan
    """

    fullscreen: bool = False
    connected: bool = False
    simulator_running: bool = False
    mission_time: float = 0.0
    fps: int = FPS

runtime = RuntimeConfig()