import numpy as np

from .shooting_methods import residual_func, shoot_trajectory_kernel, strike_methods


class LunarSystemSolver:
    def __init__(self, init_cond: list, end_cond: list, args: list):
        self.init_cond = np.array(init_cond, dtype=np.float64)  # [m0, v0, h0]
        self.end_cond = np.array(end_cond, dtype=np.float64)    # [vtau, htau]

        drym = init_cond[0] - args[2] + args[0] * args[1]
        self.phys_params = (float(args[0]), float(args[1]), float(drym))  # (thrust, k, drym)

        self.state_history = None
        self.free_fall_phase = np.zeros((4, 1), dtype=np.float64)

        self.is_dynamic_g = False
        self.dt = 1.0

        self.final_vel = None
        self.final_alt = None

    def solve(self, is_dynamic_g: bool = False, dt: float = 1.0, eps: float = 1e-5):
        self.is_dynamic_g = is_dynamic_g
        self.dt = dt
        self.state_history = strike_methods(
            self.init_cond, self.end_cond, self.phys_params, self.is_dynamic_g, self.dt, eps
        )


        if self.state_history is None:
            print("System has no solution.")
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

    def find_residuals_func(self, is_dynamic_g: bool, dt: float):
        self.is_dynamic_g = is_dynamic_g
        self.dt = dt

        if np.array_equal(self.free_fall_phase, np.zeros((4, 1), dtype=np.float64)) and self.is_dynamic_g:
            self.free_fall_phase = shoot_trajectory_kernel(
                0.0,
                self.init_cond,
                self.end_cond,
                self.phys_params,
                mode=1,
                is_brake=False,
                is_dynamic_g=True,
                dt=self.dt,
            )

        self.final_vel = residual_func(
            self.is_dynamic_g, 1, self.init_cond, self.end_cond, self.free_fall_phase, self.phys_params, dt
        )
        self.final_alt = residual_func(
            self.is_dynamic_g, 0, self.init_cond, self.end_cond, self.free_fall_phase, self.phys_params, dt
        )