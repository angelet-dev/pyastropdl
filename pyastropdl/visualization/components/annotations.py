from pyastropdl.core.utils.types import MplAxes
from pyastropdl.visualization.style import COLORS, FONTS_PLOTS


def annotate_point(
    ax: MplAxes,
    xy: tuple[float, float],
    xytext: tuple[float, float],
    pcolor: str,
    text: str,
) -> None:

    x, y = xy

    bbox = {
        "boxstyle": "round, pad=0.5",
        "fc": COLORS.annotation_fc,
        "ec": COLORS.annotation_ec,
        "lw": 1.5,
        "alpha": 0.6,
    }

    arrowprops = {
        "arrowstyle": "->",
        "connectionstyle": "arc3,rad=0.2",
        "color": COLORS.text,
    }

    ax.scatter(x, y, color=pcolor, s=30, zorder=5)
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        fontproperties = FONTS_PLOTS.annotation,
        textcoords="offset points",
        arrowprops=arrowprops,
        bbox=bbox,
        color = COLORS.text,
    )
