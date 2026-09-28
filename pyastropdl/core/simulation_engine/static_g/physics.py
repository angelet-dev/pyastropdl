import numpy as np
from numba import njit

from pyastropdl.core.common.constants import G_MOON
from pyastropdl.core.utils.types import StateVector, f64, f64_1d, f64_tuple3


@njit(f64(), cache=True, inline="always")
def get_g() -> np.float64:
    return G_MOON


@njit(f64_tuple3(f64, f64_1d), cache=True, fastmath=True, inline="always")
def get_free_fall_state(
    ts: float,
    init_state: StateVector,
) -> tuple[float, float, float]:

    g = get_g()
    m0, v0, h0 = init_state[0], init_state[1], init_state[2]
    h = -(g * ts**2) / 2.0 + v0 * ts + h0
    v = -g * ts + v0
    return (m0, v, h)


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
            state[1]
        )
    else:
        return (0.0, -g, state[1])


