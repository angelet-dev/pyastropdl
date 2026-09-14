import numpy as np
from numba import njit
from numpy.typing import NDArray

from ..common import (
    braking_ode,
    get_g,
    lerp,
    rk4_step_inplace,
)

__all__ = ["get_start_cond", "get_terminal_state", "get_time_boundary", "get_trajectory"]

MAX_SIMULATION_STEPS = 1000000


@njit(cache=True)
def get_start_cond(
    ts: float,
    init_state: NDArray[np.float64],
) -> NDArray[np.float64]:

    g = get_g()
    m0, v0, h0 = init_state[0], init_state[1], init_state[2]
    h = -(g * ts**2) / 2.0 + v0 * ts + h0
    v = -g * ts + v0
    return (m0, v, h)


@njit(cache=True)
def get_terminal_state(
    ts: float,
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    mode: int = 0,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    # mode: 0 - simulate until velocity crosses zero (v(ts, tau) = 0)
    # mode: 1 - simulate until altitude crosses zero (h(ts, tau) = 0) 

    drym = phys_params[2]
    g = get_g()

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    curr_state[:3] = get_start_cond(ts, init_state)
    curr_state[3] = ts

    for _ in range(MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

        rk4_step_inplace(braking_ode, prev_state, curr_state, phys_params, g, dt)

        cross_v = (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0
        cross_h = (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0

        if (cross_v and mode == 0) or (cross_h and mode == 1):
            return lerp(mode, end_state, curr_state, prev_state)

        elif curr_state[2] < 0 and curr_state[0] <= drym:    
        # elif curr_state[1] < prev_state[1] and curr_state[0] <= drym:
            curr_state[3] = np.nan
            return curr_state

    curr_state[3] = np.nan
    return curr_state


@njit(cache=True)
def get_trajectory(
    ts: float,
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    mode: int = 0,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    # mode: 0 - simulate until velocity crosses zero (v(ts, tau) = 0)
    # mode: 1 - simulate until altitude crosses zero (h(ts, tau) = 0) 

    drym = phys_params[2]
    g = get_g()

    state_history = np.zeros((4, MAX_SIMULATION_STEPS), dtype=np.float64)

    curr_state = np.empty(4, dtype=np.float64)
    prev_state = np.empty(4, dtype=np.float64)

    curr_state[:3] = get_start_cond(ts, init_state)
    curr_state[3] = ts
    
    state_history[:, 0] = curr_state

    for curr_shift in range(1, MAX_SIMULATION_STEPS):
        prev_state, curr_state = curr_state, prev_state

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


@njit(cache=True)
def get_time_boundary(
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    dt: float,
) -> tuple[np.float64, np.float64]:
    
    v0, h0 = init_state[1], init_state[2]
    g = get_g()

    t_min = v0 / g if v0 > 0 else 0
    t_max = (v0 + np.sqrt(v0**2 + 2.0 * g * h0)) / g

    terminal_state = get_terminal_state(
        t_max,
        init_state,
        end_state,
        phys_params,
        dt=dt,
    )

    if np.isnan(terminal_state[3]):
        start_v, end_v = get_start_cond(t_max, init_state)[1], terminal_state[1]
        dv = end_v - start_v
        t_max = (v0 + dv) / g - 1.0

        terminal_state = get_terminal_state(
            t_max,
            init_state,
            end_state,
            phys_params,
            dt=dt,
        )

        if terminal_state[2] > 0:
            return (t_min, np.nan)

    return (t_min, t_max)




