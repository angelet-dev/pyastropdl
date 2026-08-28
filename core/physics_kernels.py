import numpy as np
from numba import njit
from numpy.typing import NDArray


@njit(cache=True)
def get_g(is_dynamic_g: bool, h: np.float64 = 0.0) -> np.float64:
    if is_dynamic_g:
        G = 6.674e-11
        M = 7.346e22
        R = 1734.4e3
        return (G * M) / (R + h) ** 2
    else:
        return 1.622

@njit(cache=True)
def dynamics_kernel(
    is_brake: bool, state: NDArray[np.float64], phys_params: tuple, g: np.float64
) -> NDArray[np.float64]:
    thrust, k, drym = phys_params
    m, v = state[0], state[1]
    dh_dt = v

    if is_brake and m >= drym:
        dv_dt = (thrust / m) - g
        dm_dt = -thrust * k
    else:
        dv_dt = -g
        dm_dt = 0.0

    return np.array([dm_dt, dv_dt, dh_dt, 1.0], dtype=np.float64)

@njit(cache=True)
def rk4_step_kernel(
    is_brake: bool,
    prev_state: NDArray[np.float64],
    phys_params: tuple,
    g: np.float64,
    dt: float,
) -> NDArray[np.float64]:
    k_1 = dynamics_kernel(is_brake, prev_state, phys_params, g)
    k_2 = dynamics_kernel(is_brake, prev_state + (dt / 2.0) * k_1, phys_params, g)
    k_3 = dynamics_kernel(is_brake, prev_state + (dt / 2.0) * k_2, phys_params, g)
    k_4 = dynamics_kernel(is_brake, prev_state + dt * k_3, phys_params, g)

    return prev_state + dt * (k_1 + 2.0 * k_2 + 2.0 * k_3 + k_4) / 6.0

@njit(cache=True)
def lerp_kernel(
    mode: int,
    end_state: NDArray[np.float64],
    curr_state: NDArray[np.float64],
    prev_state: NDArray[np.float64],
) -> NDArray[np.float64]:
    # mode: 0 - velocity, 1 - altitude
    
    match mode:
        case 0:
            dv = curr_state[1] - prev_state[1]
            theta = (end_state[0] - prev_state[1]) / dv if abs(dv) > 1e-9 else 0.0
        case 1:
            dh = curr_state[2] - prev_state[2]
            theta = (end_state[1] - prev_state[2]) / dh if abs(dh) > 1e-9 else 0.0

    return prev_state + theta * (curr_state - prev_state)