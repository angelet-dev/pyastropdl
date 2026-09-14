import numpy as np
from numba import njit
from numpy.typing import NDArray

from ..common import braking_ode, free_fall_ode, get_g, lerp, rk4_step_inplace

MAX_SIMULATION_STEPS = 900000

__all__ = ["get_ff_phase", "get_start_cond", "get_terminal_state", "get_time_boundary", "get_trajectory"]


@njit(cache=True)
def get_start_cond(
    ts: float,
    free_fall_phase: NDArray[np.float64],
    dt: float = 0.1
) -> NDArray[np.float64]:

    max_cols = free_fall_phase.shape[1]
    n = int(ts // dt)

    if n < 0 or n >= max_cols - 1 or np.isnan(free_fall_phase[3, n]):
        return np.array([np.nan, np.nan, np.nan], dtype=np.float64)

    theta = (ts - n * dt) / dt

    return free_fall_phase[:3, n] + theta * (
        free_fall_phase[:3, n + 1] - free_fall_phase[:3, n]
    )


@njit(cache=True)
def get_ff_phase( 
    init_state: NDArray[np.float64],
    phys_params: tuple,
    dt: float = 0.1,
) -> NDArray[np.float64]:
    
    free_fall_phase = np.zeros((4, MAX_SIMULATION_STEPS), dtype=np.float64)

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    curr_state[:3] = init_state[:3]
    curr_state[3] = 0.0
    
    free_fall_phase[:, 0] = curr_state

    for curr_shift in range(1, MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        g = get_g(prev_state[2], True)
        rk4_step_inplace(free_fall_ode, prev_state, curr_state, phys_params, g, dt)

        if curr_state[2] * prev_state[2] <= 0:
            end_state = np.array([0, 0], dtype=np.float64)
            free_fall_phase[:, curr_shift] = lerp(
                1, end_state, curr_state, prev_state
            )
            return free_fall_phase[:, : curr_shift + 1]

        free_fall_phase[:, curr_shift] = curr_state

    free_fall_phase[:, curr_shift] = curr_state
    free_fall_phase[3, curr_shift] = np.nan
    return free_fall_phase[:, : curr_shift + 1]


@njit(cache=True)
def get_terminal_state(
    ts: float,
    free_fall_phase: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    mode: int = 0,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    drym = phys_params[2]

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    start_cond = get_start_cond(ts, free_fall_phase, dt)
    if np.isnan(start_cond[2]):
        curr_state[3] = np.nan
        return curr_state

    curr_state[:3] = start_cond
    curr_state[3] = ts

    for _ in range(MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        g = get_g(prev_state[2], True)
        rk4_step_inplace(braking_ode, prev_state, curr_state, phys_params, g, dt)

        cross_v = (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0
        cross_h = (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0

        if (cross_v and mode == 0) or (cross_h and mode == 1):
            return lerp(mode, end_state, curr_state, prev_state)

        elif curr_state[2] < 0 and curr_state[0] <= drym:    
            curr_state[3] = np.nan
            return curr_state

    curr_state[3] = np.nan
    return curr_state


@njit(cache=True)
def get_trajectory(
    ts: float,
    free_fall_phase: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    mode: int = 0,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    drym = phys_params[2]

    state_history = np.zeros((4, MAX_SIMULATION_STEPS), dtype=np.float64)

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    start_cond = get_start_cond(ts, free_fall_phase, dt)
    if np.isnan(start_cond[2]):
        state_history[3, 0] = np.nan
        return state_history[:, :1]

    curr_state[:3] = start_cond
    curr_state[3] = ts
    
    state_history[:, 0] = curr_state

    for curr_shift in range(1, MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        g = get_g(prev_state[2], True)
        rk4_step_inplace(braking_ode, prev_state, curr_state, phys_params, g, dt)

        cross_v = (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0
        cross_h = (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0

        if (cross_v and mode == 0) or (cross_h and mode == 1):
            state_history[:, curr_shift] = lerp(
                mode, end_state, curr_state, prev_state
            )
            return state_history[:, : curr_shift + 1]

        elif curr_state[2] < 0 and curr_state[0] <= drym:
            state_history[:, curr_shift] = curr_state
            state_history[3, curr_shift] = np.nan
            return state_history[:, : curr_shift + 1]

        state_history[:, curr_shift] = curr_state

    state_history[:, curr_shift] = curr_state
    state_history[3, curr_shift] = np.nan
    return state_history[:, : curr_shift + 1]


def get_time_boundary(
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    free_fall_phase: NDArray[np.float64],
    dt: float
):
    mask = free_fall_phase[1, :] <= 0
    idx = np.flatnonzero(mask)

    if idx.size == 0:
        return (np.nan, np.nan)
    
    t_min = free_fall_phase[3, idx[0]]
    t_max = free_fall_phase[3, idx[-1]]

    terminal_state = get_terminal_state(
        t_max,
        free_fall_phase,
        end_state,
        phys_params,
        dt=dt,
    )
    
    if np.isnan(terminal_state[3]):
        v0, h0 = init_state[1], init_state[2]
        start_v, end_v = free_fall_phase[1, idx[-1]], terminal_state[1]
        dv = end_v - start_v
        g = get_g(h0 / 2, True)
        t_max = (v0 + dv) / g - 1.0

        terminal_state = get_terminal_state(
            t_max,
            free_fall_phase,
            end_state,
            phys_params,
            dt=dt,
        )

        if np.isnan(terminal_state[3]) or terminal_state[2] > 0:
            return (t_min, np.nan)

    return (t_min, t_max)