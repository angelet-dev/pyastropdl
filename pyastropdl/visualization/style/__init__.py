from .axes import (
    set_back_grid,
    set_phase_trajectory,
    set_residual,
    set_time_series_telemetry,
    set_video,
)
from .colors import COLORS, Palette
from .fonts import FONTS_PLOTS, FONTS_VIDEO
from .themes import apply_dark_theme

__all__ = [
    "COLORS",
    "FONTS_PLOTS",
    "FONTS_VIDEO",
    "Palette",
    "apply_dark_theme",
    "set_back_grid",
    "set_phase_trajectory",
    "set_residual",
    "set_time_series_telemetry",
    "set_video",
]
