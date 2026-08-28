import numpy as np
from numba import njit
from numpy.typing import NDArray

from .physics_kernels import get_g, lerp_kernel, rk4_step_kernel
from .root_finding import halley_method

MAX_SIMULATION_STEPS = 900000
MAX_RESIDUAL_STEPS = 100000


@njit(cache=True)
def get_start_cond(
    ts: float,
    init_state: NDArray[np.float64],
    free_fall_phase: NDArray[np.float64],
    is_dynamic_g: bool = False,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    if is_dynamic_g:
        n = int(ts // dt)
        theta = (ts - n * dt) / dt
        return free_fall_phase[:3, n] + theta * (
            free_fall_phase[:3, n + 1] - free_fall_phase[:3, n]
        )
    else:
        g = get_g(is_dynamic_g)
        m0, v0, h0 = init_state[0], init_state[1], init_state[2]
        h = -(g * ts**2) / 2.0 + v0 * ts + h0
        v = -g * ts + v0
        return np.array([m0, v, h], dtype=np.float64)


@njit(cache=True)
def get_time_boundary(
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    free_fall_phase: NDArray[np.float64],
    is_dynamic_g: bool,
    dt: float,
    eps: float,
):
    v0, h0 = init_state[1], init_state[2]

    if is_dynamic_g:
        mask = free_fall_phase[1, :] <= 0
        idx = np.flatnonzero(mask)
        t_min = free_fall_phase[3, idx[0]]
        t_max = free_fall_phase[3, idx[-1]]
    else:
        g = get_g(is_dynamic_g)
        t_min = v0 / g + eps if v0 > 0 else eps
        t_max = (v0 + np.sqrt(v0**2 + 2.0 * g * h0)) / g

    state_history = shoot_trajectory_kernel(
        t_max,
        init_state,
        end_state,
        phys_params,
        free_fall_phase,
        is_dynamic_g=is_dynamic_g,
        dt=dt,
    )

    if state_history[3, -1] == np.inf:
        start_v, end_v = state_history[1, 0], state_history[1, -2]
        dv = end_v - start_v
        g = get_g(is_dynamic_g, h0 // 2)
        t_max = (v0 + dv) / g - 1.0

        start_cond = get_start_cond(
            t_max, init_state, free_fall_phase, is_dynamic_g, dt
        )
        state_history = shoot_trajectory_kernel(
            t_max,
            start_cond,
            end_state,
            phys_params,
            free_fall_phase,
            is_dynamic_g=is_dynamic_g,
            dt=dt,
        )

        if state_history[2, -1] > 0:
            return (None, None)

    return (t_min, t_max)


@njit(cache=True)
def shoot_terminal_kernel(
    ts: float,
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    free_fall_phase: NDArray[np.float64],
    mode: int = 0,
    is_brake: bool = True,
    is_dynamic_g: bool = False,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    drym = phys_params[2]

    curr_state = np.empty(4, dtype=np.float64)
    curr_state[:3] = get_start_cond(ts, init_state, free_fall_phase, is_dynamic_g, dt)
    curr_state[3] = ts

    while True:
        prev_state = curr_state.copy()

        g = get_g(is_dynamic_g, prev_state[2])
        curr_state = rk4_step_kernel(is_brake, prev_state, phys_params, g, dt)

        cross_v = (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0
        cross_h = (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0

        if (cross_v and mode == 0) or (cross_h and mode == 1):
            return lerp_kernel(mode, end_state, curr_state, prev_state)

        elif curr_state[2] < 0 and curr_state[0] <= drym:
            curr_state[3] = np.inf
            return curr_state


@njit(cache=True)
def shoot_trajectory_kernel(
    ts: float,
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    free_fall_phase: NDArray[np.float64],
    mode: int = 0,
    is_brake: bool = True,
    is_dynamic_g: bool = False,
    dt: float = 0.1,
) -> NDArray[np.float64]:

    drym = phys_params[2]

    start_cond = get_start_cond(ts, init_state, free_fall_phase, is_dynamic_g, dt)

    state_history = np.zeros((4, MAX_SIMULATION_STEPS), dtype=np.float64)
    state_history[:3, 0] = start_cond
    state_history[3, 0] = ts

    curr_shift = 0

    while True:
        prev_state = state_history[:, curr_shift]
        curr_shift += 1

        g = get_g(is_dynamic_g, prev_state[2])
        curr_state = rk4_step_kernel(is_brake, prev_state, phys_params, g, dt)

        cross_v = (curr_state[1] - end_state[0]) * (prev_state[1] - end_state[0]) <= 0
        cross_h = (curr_state[2] - end_state[1]) * (prev_state[2] - end_state[1]) <= 0

        if (cross_v and mode == 0) or (cross_h and mode == 1):
            state_history[:, curr_shift] = lerp_kernel(
                mode, end_state, curr_state, prev_state
            )
            return state_history[:, : curr_shift + 1]

        elif curr_state[2] < 0 and curr_state[0] <= drym:
            state_history[:, curr_shift] = curr_state
            state_history[3, curr_shift] = np.inf
            return state_history[:, : curr_shift + 1]

        state_history[:, curr_shift] = curr_state


@njit(cache=True)
def altitude_residual_wrapper(ts: float, args: tuple) -> float:
    init_state, end_state, phys_params, free_fall_phase, is_dynamic_g, dt = args

    terminal_state = shoot_terminal_kernel(
        ts,
        init_state,
        end_state,
        phys_params,
        free_fall_phase,
        is_brake=True,
        is_dynamic_g=is_dynamic_g,
        dt=dt,
    )
    return terminal_state[2]


@njit(cache=True)
def strike_methods(
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    is_dynamic_g: bool = False,
    dt: float = 1.0,
    eps: float = 1e-5,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:

    if is_dynamic_g:
        free_fall_phase = shoot_trajectory_kernel(
            0.0,
            init_state,
            end_state,
            phys_params,
            np.zeros((4, 1)),
            mode=1,
            is_brake=False,
            is_dynamic_g=True,
            dt=dt,
        )
    else:
        free_fall_phase = np.zeros((4, 1), dtype=np.float64)

    t_bounds = get_time_boundary(
        init_state, end_state, phys_params, free_fall_phase, is_dynamic_g, dt, eps
    )

    func_args = (init_state, end_state, phys_params, free_fall_phase, is_dynamic_g, dt)

    optimal_ts = halley_method(altitude_residual_wrapper, func_args, t_bounds, eps=eps)

    state_history = shoot_trajectory_kernel(
        optimal_ts,
        init_state,
        end_state,
        phys_params,
        free_fall_phase,
        mode=1,
        is_brake=True,
        is_dynamic_g=is_dynamic_g,
        dt=dt,
    )

    return state_history


@njit(cache=True)
def residual_func(
    is_dynamic_g: bool,
    mode: int,
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    free_fall_phase: NDArray[np.float64],
    phys_params: tuple,
    dt: float = 1.0,
) -> NDArray[np.float64]:

    func_state = np.zeros((2, MAX_RESIDUAL_STEPS), dtype=np.float64)
    func_state[0, 0] = np.inf

    curr_shift = 0
    curr_ts = 0.0
    max_ts = free_fall_phase[3, -1]

    while True:
        terminal_state = shoot_terminal_kernel(
            curr_ts,
            init_state,
            end_state,
            phys_params,
            free_fall_phase,
            mode=mode,
            is_dynamic_g=is_dynamic_g,
            dt=dt,
        )

        if (
            terminal_state[3] == np.inf and func_state[0, 0] != np.inf
        ) or curr_shift >= MAX_RESIDUAL_STEPS - 1:
            break

        elif terminal_state[3] != np.inf:
            func_state[0, curr_shift] = (
                terminal_state[2] if mode == 0 else terminal_state[1]
            )
            func_state[1, curr_shift] = curr_ts
            curr_shift += 1

        curr_ts += dt
        if curr_ts > max_ts and is_dynamic_g:
            break

    return func_state[:, :curr_shift]
