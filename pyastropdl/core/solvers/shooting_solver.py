import numpy as np
from numba import njit

import pyastropdl.core.simulation_engine.dynamic_g as dg
import pyastropdl.core.simulation_engine.static_g as sg
from pyastropdl.core.utils import (
    FloatArray,
    StateVector,
    f64,
    f64_1d,
    f64_2d_bool,
    f64_tuple3,
    nb_str,
)


@njit(f64_2d_bool(f64_1d, f64_1d, f64_tuple3, nb_str, f64, f64), cache=True)
def shooting_method(
    init_state: StateVector,
    end_state: StateVector,
    phys_params: tuple,
    sim_engine: str,
    dt: float,
    eps: float,
) -> tuple[FloatArray, bool]:


    if sim_engine == 'static_g':
        t_bounds = sg.get_time_boundary(
            init_state, end_state, phys_params, dt
        )

        if np.isnan(t_bounds[1]):
            return (np.empty((4,2), dtype=np.float64), False)
        
        optimal_ts = sg.halley_method(init_state, end_state, phys_params, dt, t_bounds, eps=eps)
        if np.isnan(optimal_ts):
            return (np.empty((4,2), dtype=np.float64), False)
        
        state_history, _ = sg.get_trajectory(
            optimal_ts,
            init_state,
            end_state,
            phys_params,
            mode=0,
            dt=dt,
        )

        return (state_history, True)

    elif sim_engine == 'dynamic_g':

        free_fall_phase, _ = dg.get_ff_phase(init_state, dt)

        t_bounds = dg.get_time_boundary(
            init_state, end_state, phys_params, free_fall_phase, dt
        )

        if np.isnan(t_bounds[1]):
            return (np.empty((4,2), dtype=np.float64), False)
        
        optimal_ts = dg.halley_method(free_fall_phase, end_state, phys_params, dt, t_bounds, eps=eps)

        if np.isnan(optimal_ts):
            return (np.empty((4,2), dtype=np.float64), False)
        
        state_history, _ = dg.get_trajectory(
            optimal_ts,
            free_fall_phase,
            end_state,
            phys_params,
            mode=0,
            dt=dt,
        )

        return (state_history, True)

    else:
        return (np.empty((4,2), dtype=np.float64), False)