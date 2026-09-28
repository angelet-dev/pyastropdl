import numpy as np
from numba import njit

from pyastropdl.core.utils.types import StateVector, f64, f64_1d, f64_tuple3, void

from .physics import braking_ode, free_fall_ode


@njit(void(f64_1d, f64_1d, f64_tuple3, f64, f64), cache=True, fastmath=True)
def rk4_bp_inplace(
    curr_state: StateVector,
    prev_state: StateVector,
    phys_params: tuple,
    g: np.float64,
    dt: float,
) -> None:

    # phys_params mapping: (thrust, k, drym) = (phys_params[0], phys_params[1], phys_params[2])
    # state mapping: (m, v, h) = (_state[0], _state[1], _state[2])

    m_dot = phys_params[0] * phys_params[1]
    fuel_remaining = prev_state[0] - phys_params[2]

    if 0.0 < fuel_remaining < m_dot * dt:
        dt = fuel_remaining / m_dot

    dt_half = dt * 0.5

    k10, k11, k12 = braking_ode(prev_state, phys_params, g)

    curr_state[0] = prev_state[0] + dt_half * k10
    curr_state[1] = prev_state[1] + dt_half * k11
    curr_state[2] = prev_state[2] + dt_half * k12
    k20, k21, k22 = braking_ode(curr_state, phys_params, g)

    curr_state[0] = prev_state[0] + dt_half * k20
    curr_state[1] = prev_state[1] + dt_half * k21
    curr_state[2] = prev_state[2] + dt_half * k22
    k30, k31, k32 = braking_ode(curr_state, phys_params, g)

    curr_state[0] = prev_state[0] + dt * k30
    curr_state[1] = prev_state[1] + dt * k31
    curr_state[2] = prev_state[2] + dt * k32
    k40, k41, k42 = braking_ode(curr_state, phys_params, g)

    inv_six = 1.0/6.0

    curr_state[0] = prev_state[0] + dt * (k10 + 2.0 * k20 + 2.0 * k30 + k40) * inv_six
    curr_state[1] = prev_state[1] + dt * (k11 + 2.0 * k21 + 2.0 * k31 + k41) * inv_six
    curr_state[2] = prev_state[2] + dt * (k12 + 2.0 * k22 + 2.0 * k32 + k42) * inv_six
    curr_state[3] = prev_state[3] + dt


@njit(void(f64_1d, f64_1d, f64, f64), cache=True, fastmath=True)
def rk4_ffp_inplace(
    curr_state: StateVector,
    prev_state: StateVector,
    g: np.float64,
    dt: float,
) -> None:

    # state mapping: (m, v, h) = (_state[0], _state[1], _state[2])

    dt_half = dt * 0.5

    k10, k11, k12 = free_fall_ode(prev_state, g)

    curr_state[0] = prev_state[0] + dt_half * k10
    curr_state[1] = prev_state[1] + dt_half * k11
    curr_state[2] = prev_state[2] + dt_half * k12
    k20, k21, k22 = free_fall_ode(curr_state, g)

    curr_state[0] = prev_state[0] + dt_half * k20
    curr_state[1] = prev_state[1] + dt_half * k21
    curr_state[2] = prev_state[2] + dt_half * k22
    k30, k31, k32 = free_fall_ode(curr_state, g)

    curr_state[0] = prev_state[0] + dt * k30
    curr_state[1] = prev_state[1] + dt * k31
    curr_state[2] = prev_state[2] + dt * k32
    k40, k41, k42 = free_fall_ode(curr_state, g)

    inv_six = 1.0/6.0

    curr_state[0] = prev_state[0] + dt * (k10 + 2.0 * k20 + 2.0 * k30 + k40) * inv_six
    curr_state[1] = prev_state[1] + dt * (k11 + 2.0 * k21 + 2.0 * k31 + k41) * inv_six
    curr_state[2] = prev_state[2] + dt * (k12 + 2.0 * k22 + 2.0 * k32 + k42) * inv_six
    curr_state[3] = prev_state[3] + dt


