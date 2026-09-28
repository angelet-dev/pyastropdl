import numpy as np
from numba import njit

from pyastropdl.core.common.constants import MAX_SIMULATION_STEPS
from pyastropdl.core.common.interpolation import lerp_inplace
from pyastropdl.core.utils.types import (
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

from .integrators import rk4_bp_inplace
from .physics import get_free_fall_state, get_g


@njit(f64_tuple2(f64_1d), cache=True, fastmath=True)
def get_theo_time_boundary(
    init_state: StateVector,
) -> tuple[np.float64, np.float64]:
    
    v0, h0 = init_state[1], init_state[2]
    g = get_g()

    t_min = v0 / g if v0 > 0 else 0
    t_max = (v0 + np.sqrt(v0**2 + 2.0 * g * h0)) / g

    return (t_min, t_max)

@njit(f64_2d(f64_1d, f64), cache=True)
def get_ff_phase(init_state: StateVector, dt: float) -> FloatArray:

    _, t_max = get_theo_time_boundary(init_state)

    N = int(t_max/dt)

    free_fall_phase = np.zeros((N, 4), dtype=np.float64).T

    t = np.linspace(0.0, t_max, N)
    free_fall_phase[3, :] = t

    m0, v0, h0 = init_state[0], init_state[1], init_state[2]
    g = get_g()

    free_fall_phase[0, :] = m0
    free_fall_phase[1, :] = v0 - g * t
    free_fall_phase[2, :] = h0 + v0 * t - 0.5 * g * (t ** 2)

    return free_fall_phase


@njit(f64_1d_bool(f64, f64_1d, f64_1d, f64_tuple3, i64, f64), cache=True, fastmath=True)
def get_terminal_state(
    ts: float,
    init_state: StateVector,
    end_state: StateVector,
    phys_params: tuple,
    mode: int,
    dt: float,
) -> tuple[StateVector, bool]:

    # mode: 0 - simulate until velocity crosses zero (v(ts, tau) = 0)
    # mode: 1 - simulate until altitude crosses zero (h(ts, tau) = 0) 

    drym = phys_params[2]
    g = get_g()

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    curr_state[:3] = get_free_fall_state(ts, init_state)
    curr_state[3] = ts

    for _ in range(MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

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
        # elif curr_state[1] < prev_state[1] and curr_state[0] <= drym:
            return (curr_state, False)

    return (curr_state, False)


@njit(f64_2d_bool(f64, f64_1d, f64_1d, f64_tuple3, i64, f64), cache=True, fastmath=True)
def get_trajectory(
    ts: float,
    init_state: StateVector,
    end_state: StateVector,
    phys_params: tuple,
    mode: int,
    dt: float,
) -> tuple[FloatArray, bool]:

    # mode: 0 - simulate until velocity crosses zero (v(ts, tau) = 0)
    # mode: 1 - simulate until altitude crosses zero (h(ts, tau) = 0) 

    drym = phys_params[2]
    g = get_g()

    state_history = np.zeros((MAX_SIMULATION_STEPS, 4), dtype=np.float64).T

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    curr_state[0], curr_state[1], curr_state[2] = get_free_fall_state(ts, init_state)
    curr_state[3] = ts
    
    state_history[:, 0] = curr_state

    for curr_shift in range(1, MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

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


@njit(f64_tuple2(f64_1d, f64_1d, f64_tuple3, f64), cache=True)
def get_time_boundary(
    init_state: StateVector,
    end_state: StateVector,
    phys_params: tuple,
    dt: float,
) -> tuple[np.float64, np.float64]:
    
    v0, h0 = init_state[1], init_state[2]
    g = get_g()

    t_min = v0 / g if v0 > 0.0 else 0.0
    t_max = (v0 + np.sqrt(v0**2 + 2.0 * g * h0)) / g

    terminal_state, valid = get_terminal_state(
        t_max,
        init_state,
        end_state,
        phys_params,
        0,
        dt=dt,
    )

    if not valid:
        start_v, end_v = get_free_fall_state(t_max, init_state)[1], terminal_state[1]
        dv = end_v - start_v
        t_max = (v0 + dv) / g - 1.0

        terminal_state, valid = get_terminal_state(
            t_max,
            init_state,
            end_state,
            phys_params,
            0,
            dt,
        )

        if terminal_state[2] > 0 or not valid:
            return (t_min, np.nan)

    return (t_min, t_max)




