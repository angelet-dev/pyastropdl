import numpy as np
from numba import njit
from numpy import nan

from pyastropdl.core.common.constants import MAX_ITERATIONS_STEPS
from pyastropdl.core.utils.types import (
    StateVector,
    f64,
    f64_1d,
    f64_2d,
    f64_tuple2,
    f64_tuple3,
)

from .residuals import altitude_residual


@njit(f64(f64_2d, f64_1d, f64_tuple3, f64, f64_tuple2, f64), cache=True)
def halley_method(
    free_fall_phase: StateVector,
    end_state: StateVector,
    phys_params: tuple[float, float, float],
    dt: float,
    t_bounds: tuple[float, float],
    eps: float = 1e-5,
) -> float:

    t_min, t_max = t_bounds
    ti = t_max

    for _ in range(MAX_ITERATIONS_STEPS):
        
        f_val = altitude_residual(ti, free_fall_phase, end_state, phys_params, dt)
        if abs(f_val) <= eps:
            return ti

        f_left = altitude_residual(ti - eps, free_fall_phase, end_state, phys_params, dt)
        f_right = altitude_residual(ti + eps, free_fall_phase, end_state, phys_params, dt)

        f_dx = (f_right - f_left) / (2.0 * eps)
        f_ddx = (f_right - 2.0 * f_val + f_left) / (eps**2)

        denominator = 2.0 * (f_dx**2) - f_val * f_ddx

        
        if abs(denominator) < 1e-12:
            return nan

        ti += -(2.0 * f_val * f_dx) / denominator

        if np.isnan(ti):
            return nan
        
        if ti >= t_max:
            ti = t_max - eps
            t_max -= 0.1
        elif ti <= t_min:
            ti = t_min + eps
            t_min += 0.1

    return nan

