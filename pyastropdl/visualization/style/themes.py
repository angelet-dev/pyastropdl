from collections.abc import Iterable

from matplotlib.figure import Figure

from pyastropdl.core.utils.types import MplAxes

from .colors import COLORS
from .fonts import FONTS_PLOTS


def style_legend(ax: MplAxes) -> None:

    legend = ax.get_legend()
    if legend is None:
        return

    frame = legend.get_frame()
    frame.set_facecolor(COLORS.legend_fc)
    frame.set_edgecolor(COLORS.legend_ec)
    frame.set_linewidth(1.0)
    frame.set_alpha(0.75)


    for text in legend.get_texts():
        text.set_color(COLORS.text)
        text.set_fontproperties(FONTS_PLOTS.legend)


def apply_dark_theme(fig: Figure, axes: MplAxes | tuple[MplAxes, ...]) -> None:
    
    fig.set_facecolor(COLORS.bg_main)

    axes_list = list(axes) if isinstance(axes, Iterable) else [axes]

    for ax in axes_list:
        ax.set_facecolor(COLORS.bg_axes)
        
        ax.spines["left"].set_color(COLORS.white)
        ax.spines["left"].set_position(("axes", -0.03))
        ax.spines["bottom"].set_color(COLORS.white)
        ax.spines["bottom"].set_position(("axes", -0.03))
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        
        ax.tick_params(
            axis="both", which="both", direction="out", 
            length=6, width=1.2, pad=5, colors=COLORS.text
        )
        ax.grid(True, color=COLORS.grid, linestyle='-', alpha=1)
        
        ax.xaxis.label.set_color(COLORS.text)
        ax.yaxis.label.set_color(COLORS.text)
        
        ax.title.set_color(COLORS.text)
        ax.title.set_fontproperties(FONTS_PLOTS.title)
        
        ax.xaxis.label.set_fontproperties(FONTS_PLOTS.axis_label)
        
        ax.yaxis.label.set_fontproperties(FONTS_PLOTS.axis_label)

        style_legend(ax)
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(FONTS_PLOTS.tick)
