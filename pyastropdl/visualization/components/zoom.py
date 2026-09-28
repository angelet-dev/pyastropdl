from matplotlib.ticker import AutoLocator

from pyastropdl.core.utils.types import MplAxes


def target_zoom(
    ax: MplAxes, 
    start_center: tuple[float, float], 
    target_center: tuple[float, float],
    view_bounds: tuple[float, float, float, float], 
    curr_frame: int, 
    total_frames: int, 
    
) -> None:

    x1, y1 = start_center
    x2, y2 = target_center

    dx1, dy1, dx2, dy2 = view_bounds

    norm = curr_frame/total_frames
    norm = 1 - 2**(-10*norm) 

    new_x = -x2*norm - x1*(1-norm)
    new_y = y2*norm + y1*(1-norm)

    new_dx = dx2*norm + dx1*(1-norm)
    new_dy = dy2*norm + dy1*(1-norm)

    ax.set_xlim(new_x - new_dx, new_x + new_dx)
    ax.set_ylim(new_y - new_dy, new_y + new_dy)

    ax.xaxis.set_major_locator(AutoLocator())
    ax.yaxis.set_major_locator(AutoLocator())
