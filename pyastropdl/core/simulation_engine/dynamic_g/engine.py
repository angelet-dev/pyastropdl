import numpy as np
from numba import njit

from pyastropdl.core.common.constants import MAX_SIMULATION_STEPS
from pyastropdl.core.common.interpolation import lerp_inplace
from pyastropdl.core.utils import (
    FloatArray,
    StateVector,
    f64,
    f64_1d,
    f64_1d_bool,
    f64_2d,
    f64_2d_bool,
    f64_tuple2,
    f64_tuple3,
    i64,
)

from .integrators import rk4_bp_inplace, rk4_ffp_inplace
from .physics import get_g


@njit(f64_1d_bool(f64, f64_2d, f64), cache=True, fastmath=True)
def get_start_cond(
    ts: float,
    free_fall_phase: FloatArray,
    dt: float
) -> tuple[StateVector, bool]:

    max_cols = free_fall_phase.shape[1]
    n = int(ts // dt)

    res = np.empty(3, dtype=np.float64)

    if n < 0 or n >= max_cols - 1:
        return (res, False)

    theta = (ts - n * dt) / dt

    res[0] = free_fall_phase[0, n] + theta * (free_fall_phase[0, n + 1] - free_fall_phase[0, n])
    res[1] = free_fall_phase[1, n] + theta * (free_fall_phase[1, n + 1] - free_fall_phase[1, n])
    res[2] = free_fall_phase[2, n] + theta * (free_fall_phase[2, n + 1] - free_fall_phase[2, n])

    return (res, True)


@njit(f64_2d_bool(f64_1d, f64), cache=True, fastmath=True)
def get_ff_phase( 
    init_state: StateVector,
    dt: float
) -> tuple[FloatArray, bool]:
    
    free_fall_phase = np.zeros((MAX_SIMULATION_STEPS, 4), dtype=np.float64).T

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    curr_state[:3] = init_state[:3]
    curr_state[3] = 0.0
    
    free_fall_phase[:, 0] = curr_state

    for curr_shift in range(1, MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        g = get_g(prev_state[2])
        rk4_ffp_inplace(curr_state, prev_state, g, dt)

        if curr_state[2] * prev_state[2] <= 0:
            end_state = np.array([0, 0], dtype=np.float64)
            lerp_inplace(
                curr_state, prev_state, end_state, 1 
            )
            free_fall_phase[:, curr_shift] = curr_state
            return (free_fall_phase[:, : curr_shift + 1], True)

        free_fall_phase[:, curr_shift] = curr_state

    free_fall_phase[:, curr_shift] = curr_state
    return (free_fall_phase[:, : curr_shift + 1], False)


@njit(f64_1d_bool(f64, f64_2d, f64_1d, f64_tuple3, i64, f64), cache=True, fastmath=True)
def get_terminal_state(
    ts: float,
    free_fall_phase:FloatArray,
    end_state: StateVector,
    phys_params: tuple,
    mode: int,
    dt: float
) -> tuple[StateVector, bool]:

    drym = phys_params[2]

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    start_cond, valid = get_start_cond(ts, free_fall_phase, dt)
    if not valid:
        return (curr_state, False)

    curr_state[:3] = start_cond
    curr_state[3] = ts

    for _ in range(MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        g = get_g(prev_state[2])
        rk4_bp_inplace(curr_state, prev_state, phys_params, g, dt)

        if mode == 0:
            if (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0:
                lerp_inplace(curr_state, prev_state, end_state, mode)
                return (curr_state, True)
        elif mode == 1:
            if (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0:
                lerp_inplace(curr_state, prev_state, end_state, mode)
                return (curr_state, True)

        elif curr_state[2] < 0 and curr_state[0] <= drym: 
            return (curr_state, False)

    return (curr_state, False)


@njit(f64_2d_bool(f64, f64_2d, f64_1d, f64_tuple3, i64, f64), cache=True, fastmath=True)
def get_trajectory(
    ts: float,
    free_fall_phase: FloatArray,
    end_state: StateVector,
    phys_params: tuple,
    mode: int,
    dt: float
) -> tuple[FloatArray, bool]:

    drym = phys_params[2]

    state_history = np.zeros((MAX_SIMULATION_STEPS, 4), dtype=np.float64).T

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    start_cond, valid = get_start_cond(ts, free_fall_phase, dt)
    if not valid:
        return (state_history[:, :1], False)

    curr_state[:3] = start_cond
    curr_state[3] = ts
    
    state_history[:, 0] = curr_state

    for curr_shift in range(1, MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        g = get_g(prev_state[2])
        rk4_bp_inplace(curr_state, prev_state, phys_params, g, dt)

        if mode == 0:
            if (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0:
                lerp_inplace(curr_state, prev_state, end_state, mode)
                state_history[:, curr_shift] = curr_state
                return (state_history[:, : curr_shift + 1], True)
        elif mode == 1:
            if (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0:
                lerp_inplace(curr_state, prev_state, end_state, mode)
                state_history[:, curr_shift] = curr_state
                return (state_history[:, : curr_shift + 1], True)

        elif curr_state[2] < 0 and curr_state[0] <= drym:
            state_history[:, curr_shift] = curr_state
            return (state_history[:, : curr_shift + 1], False)

        state_history[:, curr_shift] = curr_state

    state_history[:, curr_shift] = curr_state
    return (state_history[:, : curr_shift + 1], False)


@njit(f64_tuple2(f64_1d, f64_1d, f64_tuple3, f64_2d, f64), cache=True)
def get_time_boundary(
    init_state: StateVector,
    end_state: StateVector,
    phys_params: tuple,
    free_fall_phase: FloatArray,
    dt: float
) -> tuple[float, float]:
    
    mask = free_fall_phase[1, :] <= 0
    idx = np.flatnonzero(mask)

    if idx.size == 0:
        return (np.nan, np.nan)
    
    t_min = free_fall_phase[3, idx[0]]
    impact_time = free_fall_phase[3, idx[-1]]
    t_max = impact_time  

    terminal_state, valid = get_terminal_state(
        impact_time, free_fall_phase, end_state, phys_params, 0, dt
    )

    if not valid:
        v0, h0 = init_state[1], init_state[2]
        start_v, end_v = free_fall_phase[1, idx[-1]], terminal_state[1]
        dv = end_v - start_v
        g = get_g(h0 / 2)
        t_max = (v0 + dv) / g

        terminal_state, valid = get_terminal_state(
            t_max, free_fall_phase, end_state, phys_params, 0, dt
        )
        
        if not valid or terminal_state[2] > 0:
            return (t_min, np.nan)

    return (t_min, t_max)