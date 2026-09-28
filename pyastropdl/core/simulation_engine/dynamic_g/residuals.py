import numpy as np
from numba import njit

from pyastropdl.core.common.constants import MAX_RESIDUALS_STEPS
from pyastropdl.core.utils.types import (
    FloatArray,
    StateVector,
    f64,
    f64_1d,
    f64_2d,
    f64_tuple3,
    i64,
)

from .engine import get_terminal_state


@njit(f64_2d(f64_2d, f64_1d, f64_tuple3, f64, i64), cache=True)
def residual_func(
    free_fall_phase: FloatArray,
    end_state: StateVector,
    phys_params: tuple,
    dt: float,
    mode: int,
) -> FloatArray:

    # mode: 0 - altitude residual (h_terminal - h_target)
    # mode: 1 - velocity residual (v_terminal - v_target)

    func_state = np.empty((MAX_RESIDUALS_STEPS, 2), dtype=np.float64).T
    func_state[0, 0] = np.nan
    has_started = False
    curr_ts: float = 0.0
    curr_shift: int = 0

    for _ in range(MAX_RESIDUALS_STEPS):
        terminal_state, valid = get_terminal_state(
            curr_ts, free_fall_phase, end_state, phys_params, mode, dt
        )

        if not valid:
            if has_started:
                break

        else:
            residual = terminal_state[2 - mode] - end_state[1 - mode]
            has_started = True
            func_state[0, curr_shift] = curr_ts
            func_state[1, curr_shift] = residual
            curr_shift += 1

        curr_ts += dt

    return func_state[:, :curr_shift]


@njit(f64(f64, f64_2d, f64_1d, f64_tuple3, f64), cache=True)
def altitude_residual(
    x: float,
    free_fall_phase: FloatArray,
    end_state: StateVector,
    phys_params: tuple[float, float, float],
    dt: float,
) -> float:

    terminal_state, valid = get_terminal_state(
        x, free_fall_phase, end_state, phys_params, mode=0, dt=dt
    )
    
    if not valid:
        return np.nan

    return terminal_state[2] - end_state[1]
