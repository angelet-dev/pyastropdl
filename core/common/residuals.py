from collections.abc import Callable

import numpy as np
from numba import njit
from numpy.typing import NDArray

from ..simulation_engine import dynamic_g as dg
from ..simulation_engine import static_g as sg

__all__ = [
    "altitude_residual_dynamic",
    "altitude_residual_static",
    "velocity_residual_dynamic",
    "velocity_residual_static",
]


@njit(cache=True)
def altitude_residual_static(x: float, args: tuple) -> float:
    init_state, end_state, phys_params, dt = args

    terminal_state = sg.get_terminal_state(
        x, init_state, end_state, phys_params, mode=0, dt=dt
    )

    if np.isnan(terminal_state[3]):
        return np.nan
    
    return terminal_state[2] - end_state[1]


@njit(cache=True)
def altitude_residual_dynamic(x: float, args: tuple) -> float:
    free_fall, end_state, phys_params, dt = args

    terminal_state = dg.get_terminal_state(
        x, free_fall, end_state, phys_params, mode=0, dt=dt
    )

    if np.isnan(terminal_state[3]):
        return np.nan
    
    return terminal_state[2] - end_state[1]


@njit(cache=True)
def velocity_residual_static(x: float, args: tuple) -> float:
    init_state, end_state, phys_params, dt = args

    terminal_state = sg.get_terminal_state(
        x, init_state, end_state, phys_params, mode=1, dt=dt
    )

    if np.isnan(terminal_state[3]):
        return np.nan
    
    return terminal_state[1] - end_state[0]


@njit(cache=True)
def velocity_residual_dynamic(x: float, args: tuple) -> float:
    free_fall, end_state, phys_params, dt = args

    terminal_state = dg.get_terminal_state(
        x, free_fall, end_state, phys_params, mode=1, dt=dt
    )

    if np.isnan(terminal_state[3]):
        return np.nan
    
    return terminal_state[1] - end_state[0]


@njit
def residual_func(
    func: Callable[..., float],
    func_args: tuple,
    dt: int = 1,
    max_steps: int = 1000,
) -> NDArray[np.float64]:

    func_state = np.zeros((2, max_steps), dtype=np.float64)
    func_state[0, 0] = np.nan
    has_started = False
    curr_ts: float = 0.0
    curr_shift = 0

    for _ in range(max_steps):
        residual = func(curr_ts, func_args)

        if np.isnan(residual):
            if has_started:
                break
        else:
            has_started = True
            func_state[1, curr_shift] = residual
            func_state[0, curr_shift] = curr_ts
            curr_shift += 1

        curr_ts += dt

    return func_state[:, :curr_shift]