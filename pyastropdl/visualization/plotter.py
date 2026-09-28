import matplotlib.pyplot as plt
import numpy as np

from pyastropdl.core import Solver
from pyastropdl.core.simulation_engine import static_g as sg
from pyastropdl.core.utils import resolve_output_path
from pyastropdl.core.utils.types import PathType
from pyastropdl.visualization.components import annotate_point, piecewise_plot
from pyastropdl.visualization.style import COLORS, apply_dark_theme
from pyastropdl.visualization.style.axes import (
    set_phase_trajectory,
    set_residual,
    set_time_series_telemetry,
)

__all__ = ["Plotter"]


class Plotter:
    def __init__(self, solver: 'Solver') -> None:
        
        self.init_cond = solver.init_cond  # [m0, v0, h0]
        self.end_cond = solver.end_cond    # [vtau, htau]
        self.phys_params = solver.phys_params  # (thrust, k, drym)
        
        self.bphase = solver.state_history
        self.ffphase = solver.ffphase
        self.wbphase = solver.wbphase 

        if self.ffphase is None or self.bphase is None:
            raise ValueError("Crtitical error: Solver instance is missing phase data.")

        self.sim_engine = solver.sim_engine
        self.dt = solver.dt
        
        self.final_vel = solver.final_vel
        self.final_alt = solver.final_alt

    def _validate_phase_data(self) -> None:
        if self.bphase is None or self.ffphase is None or self.wbphase is None:
            raise ValueError("Phase data is incomplete or missing.")

    def _validate_residual_data(self) -> None:
        if self.final_vel[1, :].shape[0] == 0 or self.final_alt[1, :].shape[0] == 0:
            raise ValueError("Final velocity or altitude arrays are empty.")

    def plot_trajectory(self, fname: str | PathType = "phase_trajectory.png") -> None:
        self._validate_phase_data()

        ts = self.bphase[3, 0]

        v_free, h_free = self.ffphase[1, :], self.ffphase[2, :]
        v_brake, h_brake = self.bphase[1, :], self.bphase[2, :]
        v_crash, h_crash = self.wbphase[1, :], self.wbphase[2, :]

        v_data = (v_crash, v_brake, v_free)
        h_data = (h_crash, h_brake, h_free)

        fig, ax = plt.subplots(figsize=(8, 8))

        ax.plot(v_crash, h_crash, color=COLORS.crash, linestyle="--", linewidth=1.5, label="Without braking")
        ax.plot(v_free, h_free, color=COLORS.free_fall, linewidth=2, label="Falling phase ($u=0$)")
        ax.plot(v_brake, h_brake, color=COLORS.braking, linewidth=2, label="Braking phase ($u=u_{max}$)")
        ax.axhline(0, color=COLORS.zero_line, linestyle="--", lw=1)

        annotate_point(
            ax, xy=(v_free[-1], h_free[-1]), xytext=(50, 0), 
            pcolor=COLORS.free_fall, text=f"Activation ($t_s={ts:.1f}$ s)"
        )

        if int(h_brake[-1]) == 0 and int(v_brake[-1]) == 0:
            text = "Soft landing"
            xy = (h_brake[-1], v_brake[-1])
        else:
            text = "Target point"
            xy = (self.end_cond[0], self.end_cond[1])

        annotate_point(ax, xy=xy, xytext=(-40, 50), pcolor=COLORS.braking, text=text)

        ax.set_ylabel("Altitude $h$, m")
        ax.set_xlabel("Velocity $v$, m/s")
        ax.set_title("Spacecraft phase trajectory")
        ax.legend()

        apply_dark_theme(fig, ax)
        set_phase_trajectory(ax, v_data, h_data)
        
        fig.tight_layout()
        fig.subplots_adjust(left=0.18)
        output_path = resolve_output_path(fname)
        fig.savefig(output_path, dpi=300)
        plt.show()

    def plot_telemetry(self, fname: str = "telemetry.png") -> None:
        self._validate_phase_data()

        ts = self.bphase[3, 0]

        t_free, m_free, v_free, h_free = self.ffphase[3, :], self.ffphase[0, :], self.ffphase[1, :], self.ffphase[2, :]
        t_brake, m_brake, v_brake, h_brake = self.bphase[3, :], self.bphase[0, :], self.bphase[1, :], self.bphase[2, :]
        t_crash, m_crash, v_crash, h_crash = self.wbphase[3, :], self.wbphase[0, :], self.wbphase[1, :], self.wbphase[2, :]

        t_data = (t_crash, t_brake, t_free)
        m_data = (m_crash, m_brake, m_free)
        v_data = (v_crash, v_brake, v_free)
        h_data = (h_crash, h_brake, h_free)

        fig, (ax_m, ax_v, ax_h) = plt.subplots(3, 1, figsize=(8, 8), sharex=True)


        ax_m.plot(t_free, m_free, color=COLORS.accent_blue, linewidth=2)
        ax_m.plot(t_brake, m_brake, color=COLORS.accent_red, linewidth=2)
        ax_m.plot(t_crash, m_crash, color="gray", linestyle="--")
        ax_m.axvline(ts, color="gray", linestyle=":")
        ax_m.set_ylabel("Mass $m$, kg")
        ax_m.set_title("Mass flow dynamics")
        set_time_series_telemetry(ax_m, t_data, m_data)


        ax_v.plot(t_crash, v_crash, color="gray", linestyle="--")
        ax_v.plot(t_free, v_free, color=COLORS.accent_blue, linewidth=2, label="Free falling")
        ax_v.plot(t_brake, v_brake, color=COLORS.accent_red, linewidth=2, label="Active braking")
        ax_v.axvline(ts, color="gray", linestyle=":")
        ax_v.axhline(0, color=COLORS.zero_line, linestyle='--', linewidth=0.8)
        ax_v.set_ylabel("Velocity $v$, m/s")
        ax_v.set_title("Velocity profile")
        set_time_series_telemetry(ax_v, t_data, v_data)
        ax_v.legend()


        ax_h.plot(t_crash, h_crash, color="gray", linestyle="--")
        ax_h.plot(t_free, h_free, color=COLORS.accent_blue, linewidth=2)
        ax_h.plot(t_brake, h_brake, color=COLORS.accent_red, linewidth=2)
        ax_h.axvline(ts, color="gray", linestyle=":")
        ax_h.axhline(0, color=COLORS.zero_line, linestyle='--', linewidth=0.8)
        ax_h.set_ylabel("Altitude $h$, m")
        ax_h.set_xlabel("Time $t$, s")
        ax_h.set_title("Altitude profile")
        set_time_series_telemetry(ax_h, t_data, h_data)


        apply_dark_theme(fig, (ax_m, ax_v, ax_h))
        fig.tight_layout()
        fig.subplots_adjust(left=0.15)
        output_path = resolve_output_path(fname)
        fig.savefig(output_path, dpi=300)
        plt.show()

    def plot_residuals(self, fname: str = "residuals.png") -> None:
        self._validate_residual_data()

        ts_vel, vel_values = self.final_vel[0, :], self.final_vel[1, :]
        ts_alt, alt_values = self.final_alt[0, :], self.final_alt[1, :]

        if self.sim_engine == 'static_g':
            t_min, t_max = sg.get_time_boundary(self.init_cond, self.end_cond, self.phys_params, self.dt)
            mask_alt = (ts_alt <= t_max) & (ts_alt >= t_min) 
            ts_alt, alt_values = ts_alt[mask_alt], alt_values[mask_alt]   
            
            mask_vel = (ts_vel <= t_max) & (ts_vel >= t_min) 
            ts_vel, vel_values = ts_vel[mask_vel], vel_values[mask_vel]

        fig, (ax_v, ax_h) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

        alt_label = r"$h(t_s, \tau) \ \text{at} \ v(t_s, \tau) = 0$"
        ax_h.axhline(0, color=COLORS.zero_line, linestyle='--', linewidth=0.8)
        ax_h.plot(ts_alt, alt_values, color=COLORS.accent_blue, linewidth=2, label=alt_label)
        
        ax_h.set_ylabel("Altitude $h$, m")
        ax_h.set_xlabel("Time $t_s$, s")
        ax_h.set_title("The final altitude function plot")
        ax_h.legend(loc="upper right")
        set_residual(ax_h, ts_alt, alt_values)

        ax_v.axhline(0, color=COLORS.zero_line, linestyle='--', linewidth=0.8)
        vel_label = r"$v(t_s, \tau) \ \text{at} \ h(t_s, \tau) = 0$"
        
        if self.bphase is not None:
            ts = self.bphase[3, 0]
            op_vel = 0
            piecewise_plot(ax_v, np.vstack((ts_vel, vel_values)), ts, xy_eps=(ts, op_vel), label=vel_label, color=COLORS.accent_red)
        else:
            ax_v.plot(ts_vel, vel_values, color=COLORS.accent_red, linewidth=2, label=vel_label)
        
        ax_v.set_ylabel("Velocity $v$, m/s")
        ax_v.set_xlabel("Time $t_s$, s")
        ax_v.set_title("The final velocity function plot")
        set_residual(ax_v, ts_vel, vel_values)
        ax_v.legend(loc="lower right")

        apply_dark_theme(fig, (ax_v, ax_h))
        fig.tight_layout()
        fig.subplots_adjust(left=0.15)
        output_path = resolve_output_path(fname)
        fig.savefig(output_path, dpi=300)
        plt.show()

    # def plot_final_vel_alt_func(self, fname: str = "final_func.png") -> None:

    #     #unstable

    #     self._validate_residual_data()

    #     ts_vel, vel_values = self.final_vel[0, :], self.final_vel[1, :]
    #     ts_alt, alt_values = self.final_alt[0, :], self.final_alt[1, :]

    #     if self.bphase is None:
    #         raise ValueError("Braking phase data is missing. Unable to determine t_s.")

    #     ts = self.bphase[3, 0]
    #     t_min, t_max = sg.get_theo_time_boundary(self.init_cond)

    #     fig, (ax_v, ax_h) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
        

    #     vel_opts = sg.get_terminal_state(ts, self.init_cond, self.end_cond, self.phys_params, 1, self.dt)[0][1] 
    #     ax_v.axvline(ts, color=COLORS.grid, linestyle=":")
    #     ax_v.axhline(0, color=COLORS.zero_line, linestyle='--', linewidth=0.8)

    #     vel_label = r"$v(t_s, \tau) \ \text{at} \ h(t_s, \tau) = 0$"
    #     piecewise_plot(ax_v, self.final_vel, ts, xy_eps=(ts, vel_opts), label=vel_label, color=COLORS.accent_blue)
    #     annotate_point(ax_v, (ts, vel_opts), (-150, -25), COLORS.accent_red, "Kink at the optimal time $t_s$")     

    #     ax_v.set_ylabel("Velocity $v$, m/s")
    #     ax_v.set_xlabel("Time $t_s$, s")
    #     ax_v.set_title("The final velocity function plot")
    #     ax_v.set_xlim(right=t_max)
    #     set_residual(ax_v, ts_vel, vel_values)
    #     ax_v.legend(loc="lower right")

    #     alt_label = r"$h(t_s, \tau) \ \text{at} \ v(t_s, \tau) = 0$"      
    #     if t_min != 0.0:
    #         alt_tmin = sg.get_terminal_state(t_min, self.init_cond, self.end_cond, self.phys_params, 0, 0.1)[0][2]
    #         piecewise_plot(ax_h, self.final_alt, t_min, xy_eps=(t_min, alt_tmin), color=COLORS.accent_red, label=alt_label)
    #         annotate_point(ax_h, (t_min, alt_tmin), (30, 30), COLORS.accent_blue, r"Kink at $h(t_{min}, \tau)$")
    #         ax_h.axvline(t_min, color=COLORS.free_fall, linestyle=":", label=r"$t_{s} = t_{min}$")
    #     else:
    #         ax_h.plot(ts_alt, alt_values, color=COLORS.accent_red, linewidth=2, label=alt_label)

    #     annotate_point(ax_h, (ts, 0), (25, 25), COLORS.accent_blue, r"Optimal time $t_s$")
    #     ax_h.axhline(0, color=COLORS.zero_line, linestyle='--', linewidth=0.8)
    #     ax_h.axvline(ts, color=COLORS.grid, linestyle=":")
        
    #     ax_h.set_ylabel("Altitude $h$, m")
    #     ax_h.set_xlabel("Time $t_s$, s")
    #     ax_h.set_title("The final altitude function plot")
    #     ax_h.set_xlim(right=t_max)
    #     set_residual(ax_h, ts_alt, alt_values)
    #     ax_h.legend(loc="upper right")

    #     apply_dark_theme(fig, (ax_v, ax_h))
    #     fig.tight_layout()
    #     fig.subplots_adjust(left=0.15)
    #     fig.savefig(str(PLOTS_DIR / fname), dpi=300)
    #     plt.show()