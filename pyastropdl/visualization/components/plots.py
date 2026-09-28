import numpy as np

from pyastropdl.core.utils.types import FloatArray, MplAxes, MplLine
from pyastropdl.visualization.style.colors import COLORS


def piecewise_plot(
    ax: MplAxes,
    array: FloatArray,
    x_kink: float | None = None,
    xy_kink: tuple[float, float] | None = None,
    xy_eps: tuple[float, float] | None = None,
    label: str | None = None,
    color: str | None = None,
) -> tuple[MplLine, MplLine]:

    if color is None:
        color = COLORS.accent_blue


    if xy_kink is not None:
        kink = xy_kink[0]
    elif x_kink is not None:
        kink = x_kink 

    time_mask = array[0, : ] <= kink
    if xy_kink is None:
        x_lp = array[0, time_mask]
        y_lp = array[1, time_mask]
    else:
        x_lp = np.append(array[0, time_mask], xy_kink[0])
        y_lp = np.append(array[1, time_mask], xy_kink[1])

    if xy_eps is None:
        x_rp = array[0, ~time_mask] 
        y_rp = array[1, ~time_mask]

    else:
        x_rp = np.append([xy_eps[0]], array[0, ~time_mask]) 
        y_rp = np.append([xy_eps[1]], array[1, ~time_mask])

    lpiece, = ax.plot(x_lp, y_lp, color=color, linewidth=2)

    if label is None:
        rpiece, = ax.plot(x_rp, y_rp, color=color, linewidth=2)
    else:
        rpiece, = ax.plot(x_rp, y_rp, color=color, linewidth=2, label=label)

    return (lpiece,rpiece)