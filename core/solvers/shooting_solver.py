import numpy as np
from numpy.typing import NDArray

from ..common import altitude_residual_dynamic, altitude_residual_static
from ..common.root_finding import halley_method
from ..simulation_engine import dynamic_g as dg
from ..simulation_engine import static_g as sg


def shooting_method(
    init_state: NDArray[np.float64],
    end_state: NDArray[np.float64],
    phys_params: tuple,
    sim_engine: str = 'static_g',
    dt: float = 1.0,
    eps: float = 1e-5,
) -> NDArray[np.float64] | None:

    match sim_engine:
        case 'static_g':
            t_bounds = sg.get_time_boundary(
                init_state, end_state, phys_params, dt
            )

            if np.isnan(t_bounds[1]):
                return None
            
            func_args = (init_state, end_state, phys_params, dt)
            optimal_ts = halley_method(altitude_residual_static, func_args, t_bounds, eps=eps)
            if np.isnan(optimal_ts):
                return None
            
            state_history = sg.get_trajectory(
                optimal_ts,
                init_state,
                end_state,
                phys_params,
                mode=0,
                dt=dt,
            )

            return state_history

        case 'dynamic_g':

            free_fall_phase = dg.get_ff_phase(init_state, phys_params, dt)

            t_bounds = dg.get_time_boundary(
                init_state, end_state, phys_params, free_fall_phase, dt
            )

            if np.isnan(t_bounds[1]):
                return None
            
            func_args = (free_fall_phase, end_state, phys_params, dt)
            optimal_ts = halley_method(altitude_residual_dynamic, func_args, t_bounds, eps=eps)

            if np.isnan(optimal_ts):
                return None
            
            state_history = dg.get_trajectory(
                optimal_ts,
                free_fall_phase,
                end_state,
                phys_params,
                mode=0,
                dt=dt,
            )

            return state_history