from matplotlib.ticker import MultipleLocator

from pyastropdl.core.utils.types import FloatArray, MplAxes

from ..components.ticks import get_bounded_ticks
from .colors import COLORS
from .fonts import FONTS_PLOTS, FONTS_VIDEO


def _apply_base_spines(ax: MplAxes) -> None:

    ax.tick_params(
        axis="both", which="both", direction="out", length=6, width=1.2, pad=5
    )

    ax.grid(True)

    ax.ticklabel_format(
        axis='y',            
        style='sci',        
        scilimits=(0, 4),    
        useMathText=True,
    )


def set_time_series_telemetry(
    ax: MplAxes,
    xdata: None | FloatArray | tuple[FloatArray, ...] = None,
    ydata: None | FloatArray | tuple[FloatArray, ...] = None,
) -> None:

    _apply_base_spines(ax)
    ax.spines["left"].set_position(("axes", -0.03))
    ax.yaxis.set_label_coords(-0.13, 0.5)
    get_bounded_ticks(ax, 8, 4, xdata=xdata, ydata=ydata, pad=(0.025, 0, 0, 0.01))


def set_phase_trajectory(
    ax: MplAxes,
    xdata: None | FloatArray | tuple[FloatArray, ...] = None,
    ydata: None | FloatArray | tuple[FloatArray, ...] = None,
) -> None:
    
    _apply_base_spines(ax)

    ax.set_xlabel("Velocity $v$ [m/s]", fontproperties = FONTS_PLOTS.axis_label_trj)
    ax.set_ylabel("Altitude $h$ [m]", fontproperties = FONTS_PLOTS.axis_label_trj)

    get_bounded_ticks(ax, 8, 8, xdata=xdata, ydata=ydata, pad=(0.025, 0.025, 0.025, 0.025))

    ax.yaxis.set_label_coords(-0.16, 0.5)
    ax.title.set_fontproperties(FONTS_PLOTS.title_trj)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(FONTS_PLOTS.tick_trj)


def set_residual(
    ax: MplAxes,
    xdata: None | FloatArray | tuple[FloatArray, ...] = None,
    ydata: None | FloatArray | tuple[FloatArray, ...] = None,
) -> None:
    
    ax.yaxis.set_label_coords(-0.13, 0.5)
    _apply_base_spines(ax)
    get_bounded_ticks(ax, 10, 5, xdata=xdata, ydata=ydata, pad=(0.025, 0, 0, 0.01))


def set_video(ax: MplAxes) -> None:
    ax.tick_params(
        axis="both",
        which="both",
        direction="out",
        length=6,
        width=2,
        labelsize=15,
        pad=5,
        colors=COLORS.text  
    )

    ax.yaxis.set_label_coords(-0.22, 0.5)
    ax.set_xlabel("Velocity $v$ [m/s]", fontproperties=FONTS_VIDEO.axis_label_video, labelpad=10)
    ax.set_ylabel("Altitude $h$ [m]", fontproperties=FONTS_VIDEO.axis_label_video, labelpad=18)

    ax.spines["right"].set_position(("axes", 1.08))
    

    ax.set_facecolor(COLORS.v_axes_fc)
    ax.grid(True, color=COLORS.grid, alpha=0.4)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(FONTS_VIDEO.tick_video)


def set_back_grid(ax: MplAxes) -> None:

    ax.set_facecolor(COLORS.back_grid_fc)
    
    ax.xaxis.set_major_locator(MultipleLocator(100.0))
    ax.yaxis.set_major_locator(MultipleLocator(100.0))
    ax.set(xlim=(0, 1920), ylim=(0, 1080))
    

    ax.grid(True, color=COLORS.grid, linestyle="--", alpha=0.3)
