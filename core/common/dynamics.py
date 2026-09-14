import numpy as np
from numba import njit
from numpy.typing import NDArray

__all__ = ["braking_ode", "free_fall_ode", "get_g", "lerp", "rk4_step_inplace"]


@njit(cache=True)
def get_g(h: np.float64 = 0.0, is_dynamic_g: bool = False) -> np.float64:
    if is_dynamic_g:
        G = 6.674e-11
        M = 7.346e22
        R = 1737.4e3
        if h<=0:
            return (G * M) / (R) ** 2
        return (G * M) / (R + h) ** 2
    else:
        return 1.622

    
@njit(cache=True)
def free_fall_ode(state: NDArray[np.float64], phys_params: tuple, g: np.float64
) -> NDArray[np.float64]:

    v = state[1]
    dh_dt = v
    dv_dt = -g
    dm_dt = 0.0

    return np.array([dm_dt, dv_dt, dh_dt, 1.0], dtype=np.float64)

    
@njit(cache=True)
def braking_ode(state: NDArray[np.float64], phys_params: tuple, g: np.float64
) -> NDArray[np.float64]:
    
    thrust, k, drym = phys_params
    m, v = state[0], state[1]
    dh_dt = v

    if m > drym:
        dv_dt = (thrust / m) - g
        dm_dt = -thrust * k
    else:
        dv_dt = -g
        dm_dt = 0.0

    return np.array([dm_dt, dv_dt, dh_dt, 1.0], dtype=np.float64)


@njit(cache=True)
def rk4_step_inplace(
    func,
    prev_state: NDArray[np.float64],
    curr_state: NDArray[np.float64],
    phys_params: tuple,
    g: np.float64,
    dt: float,
) -> None:
    
    k_1 = func(prev_state, phys_params, g)
    k_2 = func(prev_state + (dt / 2.0) * k_1, phys_params, g)
    k_3 = func(prev_state + (dt / 2.0) * k_2, phys_params, g)
    k_4 = func(prev_state + dt * k_3, phys_params, g)

    curr_state[:] = prev_state + dt * (k_1 + 2.0 * k_2 + 2.0 * k_3 + k_4) / 6.0


@njit(cache=True)
def lerp(
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