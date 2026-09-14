import numpy as np

from .common.residuals import residual_func, altitude_residual_dynamic, altitude_residual_static, velocity_residual_dynamic, velocity_residual_static
from .solvers import shooting_method
from .simulation_engine import dynamic_g as dg


class LunarSystemSolver:
    def __init__(self, init_cond: list, end_cond: list, args: list):

        self.init_cond = np.array(init_cond, dtype=np.float64)  # [m0, v0, h0]
        self.end_cond = np.array(end_cond, dtype=np.float64)    # [vtau, htau]

        drym = init_cond[0] - args[2] 
        self.phys_params = (float(args[0]), float(args[1]), float(drym))  # (thrust, k, drym)

        self.state_history = None
        self.free_fall_phase = None

        self.final_vel = None
        self.final_alt = None

    def solve(self, sim_engine: str = 'static_g', dt: float = 1.0, eps: float = 1e-5):
        self.sim_engine = sim_engine
        self.dt = dt

        self.state_history = shooting_method(
            self.init_cond, self.end_cond, self.phys_params, sim_engine, dt, eps
        )

        if self.state_history is None:
            # print("System has no solution.")
            return None
        
        return self.state_history

    def print_results(self):
        if self.state_history is None:
            print("No state history available.")
            return

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

    def find_residuals(self, sim_engine: str = 'static_g', dt: float = 1.0):

        self.sim_engine = sim_engine
        self.dt = dt

        match sim_engine:
            case 'static_g':

                # init state, end state, phys params, dt
                func_args = (self.init_cond, self.end_cond, self.phys_params, dt)

                self.final_vel = residual_func(velocity_residual_static, func_args, dt)

                self.final_alt = residual_func(altitude_residual_static, func_args, dt)

                return True

            case 'dynamic_g':

                self.free_fall_phase = dg.get_ff_phase(self.init_cond, self.phys_params, self.dt)

                # free fall phase, end state, phys params, dt
                func_args = (self.free_fall_phase, self.end_cond, self.phys_params, dt)

                self.final_vel = residual_func(velocity_residual_dynamic, func_args, dt)

                self.final_alt = residual_func(altitude_residual_dynamic, func_args, dt)

                return True