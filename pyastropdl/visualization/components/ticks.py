from matplotlib import ticker

from pyastropdl.core.utils.tools import get_data_bounds
from pyastropdl.core.utils.types import FloatArray, MplAxes


def get_bounded_ticks(
    ax: MplAxes, 
    num_xticks: int = 5, 
    num_yticks: int = 5, 
    axis: str = 'both', 
    xdata: FloatArray | tuple[FloatArray, ...] | None = None,
    ydata: FloatArray | tuple[FloatArray, ...] | None = None,
    pad: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
) -> None:

    top, bottom, left, right = pad

    if axis in ('xaxis', 'both') and xdata is not None:
        xdata_limits = get_data_bounds(xdata)
        if xdata_limits is not None and len(xdata_limits) >= 2:
            x_min, x_max = xdata_limits[0], xdata_limits[1]
            len_xdata = x_max - x_min if x_max != x_min else 1.0

            new_xmin = x_min - len_xdata * left
            new_xmax = x_max + len_xdata * right

            locator = ticker.MaxNLocator(nbins=num_xticks, steps=[1, 1.25, 2, 2.5, 4, 5, 10])
            x_ticks = locator.tick_values(new_xmin, new_xmax)

            if len(x_ticks) >= 3:
                x_step = x_ticks[1] - x_ticks[0]

                x_ticks[0] = min(x_ticks[1] - x_step * 0.6, new_xmin) 
                if abs(x_ticks[1] - new_xmin) < x_step * 0.5:
                    x_ticks[1] = (x_ticks[0] + x_ticks[2])/2
                

                x_ticks[-1] = max(x_ticks[-2] + x_step * 0.6, new_xmax)
                if abs(x_ticks[-2] - new_xmax) < x_step * 0.5:
                    x_ticks[-2] = (x_ticks[-1] + x_ticks[-3])/2


                ax.set_xticks(x_ticks)
                ax.set_xlim(x_ticks[0], x_ticks[-1])

    if axis in ('yaxis', 'both') and ydata is not None:
        ydata_limits = get_data_bounds(ydata)
        if ydata_limits is not None and len(ydata_limits) >= 2:
            y_min, y_max = ydata_limits[0], ydata_limits[1]
            len_ydata = y_max - y_min if y_max != y_min else 1.0

            new_ymin = y_min - len_ydata * bottom
            new_ymax = y_max + len_ydata * top
            locator = ticker.MaxNLocator(nbins=num_yticks, steps=[1, 1.25, 2, 2.5, 4, 5, 10])
            y_ticks = locator.tick_values(new_ymin, new_ymax)

            if len(y_ticks) >= 3:
                y_step = y_ticks[1] - y_ticks[0]

                y_ticks[0] = min(y_ticks[1] - y_step * 0.55, new_ymin) 
                if abs(y_ticks[1] - new_ymin) < y_step * 0.3:
                    y_ticks[1] = (y_ticks[0] + y_ticks[2])/2
                
                
                y_ticks[-1] = max(y_ticks[-2] + y_step, new_ymax)
                if abs(y_ticks[-2] - new_ymax) < y_step * 0.3:
                    y_ticks[-2] = (y_ticks[-1] + y_ticks[-3])/2

                ax.set_yticks(y_ticks)
                ax.set_ylim(y_ticks[0], y_ticks[-1])