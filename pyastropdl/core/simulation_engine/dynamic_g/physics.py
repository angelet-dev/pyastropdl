import numpy as np
from numba import njit

from pyastropdl.core.common.constants import GM_MOON, R_MOON
from pyastropdl.core.utils.types import StateVector, f64, f64_1d, f64_tuple3


@njit(f64(f64), cache=True, fastmath=True)
def get_g(h: np.float64 = 0.0) -> np.float64:

    if h <= 0.0:
        return GM_MOON / (R_MOON * R_MOON)
    
    r_total = R_MOON + h
    return GM_MOON / (r_total * r_total)


@njit(f64_tuple3(f64_1d, f64), cache=True, inline="always")
def free_fall_ode(
    state: StateVector, g: np.float64
) -> tuple[float, float, float]:

    # state mapping: (m, v, h) = (state[0], state[1], state[2])

    # free fall differential system state mapping:
    # dm_dt = 0.0
    # dv_dt = -g
    # dh_dt = v

    return (0.0, -g, state[1])


@njit(
    f64_tuple3(f64_1d, f64_tuple3, f64), cache=True, fastmath=True, inline="always"
)
def braking_ode(
    state: StateVector, phys_params: tuple, g: np.float64
) -> tuple[float, float, float]:

    # phys_params mapping: (thrust, k, drym) = (phys_params[0], phys_params[1], phys_params[2])
    # state mapping: (m, v, h) = (state[0], state[1], state[2])

    if state[0] > phys_params[2]:
        # dh_dt = v                   -> state[1]
        # dv_dt = (thrust / m) - g    -> (phys_params[0] / state[0]) - g
        # dm_dt = -thrust * k         -> -phys_params[0] * phys_params[1]
        return (
            -phys_params[0] * phys_params[1],
            (phys_params[0] / state[0]) - g,
            state[1],
        )
    else:
        return (0.0, -g, state[1])


