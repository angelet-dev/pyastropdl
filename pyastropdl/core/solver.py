from typing import Literal

import numpy as np

from pyastropdl.core.simulation_engine import dynamic_g as dg
from pyastropdl.core.simulation_engine import static_g as sg
from pyastropdl.core.solvers import shooting_method
from pyastropdl.core.utils.types import FloatArray, StateVector


class Solver:
    def __init__(
        self, 
        init_cond: tuple[float, float, float] | list[float], 
        end_cond: tuple[float, float] | list[float], 
        rocket_params: tuple[float, float, float] | list[float], 
        sim_engine: Literal['static_g', 'dynamic_g'] = 'static_g'
    ) -> None:

        self.init_cond: StateVector = np.array(init_cond, dtype=np.float64)  # [m0, v0, h0]
        self.end_cond: StateVector = np.array(end_cond, dtype=np.float64)    # [vtau, htau]

        drym = init_cond[0] - rocket_params[2] 
        self.phys_params: tuple[float, float, float] = (float(rocket_params[0]), float(rocket_params[1]), float(drym))  # (thrust, k, drym)

        self.sim_engine: str = sim_engine
        self.dt: float = 0.1

        self.state_history: FloatArray | None = None
        self.ffphase: FloatArray | None = None
        self.wbphase: FloatArray | None = None
        
        self.final_vel: FloatArray | None = None
        self.final_alt: FloatArray | None = None

    def solve(self, dt: float = 0.1, eps: float = 1e-5):

        self.dt = dt

        self.state_history, valid = shooting_method(
            self.init_cond, self.end_cond, self.phys_params, self.sim_engine, dt, eps
        )

        if not valid:
            self.state_history = None
            raise ValueError(
                "Critical error: Shooting method failed to find a solution for the specified initial conditions."
            )

        match self.sim_engine:
            case "static_g":
                free_fall_phase = sg.get_ff_phase(self.init_cond, self.dt)
            case "dynamic_g":
                free_fall_phase, _ = dg.get_ff_phase(self.init_cond, self.dt)

        ts = self.state_history[3,0]
        time_mask = free_fall_phase[3, :] < ts
        self.ffphase = free_fall_phase[:, time_mask]
        self.wbphase = free_fall_phase[:, ~time_mask]

        return self.state_history

    def print_results(self):
        if self.state_history is None:
            raise RuntimeError("Data not available. Execute solve() before calling print_results().")


        m_ts, v_ts, h_ts, t_s = self.state_history[:, 0]
        m_tau, v_tau, h_tau, tau = self.state_history[:, -1]

        results = f"""
        =========================================================================
                            LUNAR SOFT LANDING RESULTS                  
        =========================================================================
        Parameter          |  Engine Switching (t_s)  |  Terminal Landing (tau)
        -------------------------------------------------------------------------
        Time (s)           |  {t_s:>22.2f}  |  {tau:>22.2f}
        Altitude (m)       |  {h_ts:>22.2f}  |  {h_tau:>22.2f}
        Velocity (m/s)     |  {v_ts:>22.2f}  |  {v_tau:>22.2f}
        Vehicle Mass (kg)  |  {m_ts:>22.2f}  |  {m_tau:>22.2f}
        =========================================================================
        """
        print(results)

    def find_residuals(self, dt: float = 0.1):

        self.dt = dt

        match self.sim_engine:
            case 'static_g':

                self.final_vel = sg.residual_func(self.init_cond, self.end_cond, self.phys_params, dt, 1)

                self.final_alt = sg.residual_func(self.init_cond, self.end_cond, self.phys_params, dt, 0)

            case 'dynamic_g':

                free_fall_phase, _ = dg.get_ff_phase(self.init_cond, self.dt)

                self.final_vel = dg.residual_func(free_fall_phase, self.end_cond, self.phys_params, dt, 1)

                self.final_alt = dg.residual_func(free_fall_phase, self.end_cond, self.phys_params, dt, 0)

        return  self.final_vel, self.final_alt 

        