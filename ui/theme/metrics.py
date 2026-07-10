"""
Helicopter SAR Simulator
ui/theme/metrics.py

Design Metrics

Seluruh ukuran aplikasi berada di file ini.

Jangan pernah menggunakan angka layout secara langsung
di widget.

Author : Mas Vi & ChatGPT
"""

from __future__ import annotations

from dataclasses import dataclass


# ==========================================================
# Window
# ==========================================================

@dataclass(frozen=True)
class WindowMetrics:

    header_height: int = 60
    toolbar_height: int = 54
    statusbar_height: int = 28
    sidebar_width: int = 220


# ==========================================================
# Radius
# ==========================================================

@dataclass(frozen=True)
class RadiusMetrics:

    none: int = 0
    small: int = 6
    medium: int = 10
    large: int = 14
    extra_large: int = 20
    round: int = 999


# ==========================================================
# Spacing
# ==========================================================

@dataclass(frozen=True)
class SpacingMetrics:

    none: int = 0
    tiny: int = 4
    small: int = 8
    medium: int = 12
    large: int = 16
    extra_large: int = 24
    huge: int = 32


# ==========================================================
# Padding
# ==========================================================

@dataclass(frozen=True)
class PaddingMetrics:

    tiny: int = 4
    small: int = 8
    medium: int = 12
    large: int = 16
    extra_large: int = 24


# ==========================================================
# Icon
# ==========================================================

@dataclass(frozen=True)
class IconMetrics:

    tiny: int = 12
    small: int = 16
    medium: int = 20
    large: int = 24
    extra_large: int = 32
    huge: int = 48


# ==========================================================
# Border
# ==========================================================

@dataclass(frozen=True)
class BorderMetrics:

    thin: int = 1
    normal: int = 2
    thick: int = 3


# ==========================================================
# Shadow
# ==========================================================

@dataclass(frozen=True)
class ShadowMetrics:

    blur: int = 10
    offset_x: int = 0
    offset_y: int = 2


# ==========================================================
# Animation
# ==========================================================

@dataclass(frozen=True)
class AnimationMetrics:

    fast: int = 120
    normal: int = 180
    slow: int = 250


# ==========================================================
# Widget
# ==========================================================

@dataclass(frozen=True)
class WidgetMetrics:

    min_size: int = 10
    button_height: int = 40
    toolbar_button_height: int = 36
    card_min_height: int = 80
    slider_thickness: int = 6
    led_size: int = 10


# ==========================================================
# Card
# ==========================================================

@dataclass(frozen=True)
class CardMetrics:

    title_height: int = 32
    value_height: int = 48
    footer_height: int = 28


# ==========================================================
# Graph
# ==========================================================

@dataclass(frozen=True)
class GraphMetrics:

    grid_size: int = 25
    axis_width: int = 2
    line_width: int = 2


# ==========================================================
# Dashboard
# ==========================================================

@dataclass(frozen=True)
class DashboardMetrics:

    telemetry_card_width: int = 170
    environment_card_width: int = 170
    mission_card_width: int = 220


# ==========================================================
# Root Metrics
# ==========================================================

class Metrics:
    """
    Root Design Token.

    Example
    -------

    Metrics.spacing.medium
    Metrics.radius.large
    Metrics.icon.medium
    """

    window = WindowMetrics()
    radius = RadiusMetrics()
    spacing = SpacingMetrics()
    padding = PaddingMetrics()
    icon = IconMetrics()
    border = BorderMetrics()
    shadow = ShadowMetrics()
    animation = AnimationMetrics()
    widget = WidgetMetrics()
    card = CardMetrics()
    graph = GraphMetrics()
    dashboard = DashboardMetrics()