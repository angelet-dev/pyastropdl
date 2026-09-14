import matplotlib.pyplot as plt
import numpy as np

from core import LunarSystemSolver
from core.common.dynamics import get_g
from core.simulation_engine.dynamic_g import get_ff_phase, get_start_cond

from .customization import set_dark_theme, set_plot_costomitation


class Plotter:

    def __init__(self, solver: LunarSystemSolver):

        self.init_cond = solver.init_cond  # [m0, v0, h0]
        self.end_cond = solver.end_cond    # [vtau, htau]
        
        self.phys_params = solver.phys_params  # (thrust, k, drym)
        
        self.state_history = solver.state_history

        if solver.free_fall_phase is None and solver.sim_engine == 'dynamic_g':
            self.free_fall_phase = get_ff_phase(self.init_cond, self.phys_params, solver.dt)
        else:
            self.free_fall_phase = solver.free_fall_phase

        self.sim_engine = solver.sim_engine
        self.dt = solver.dt
        
        self.final_vel = solver.final_vel
        self.final_alt = solver.final_alt


    def plot_trajectories(self):

        set_dark_theme()

        if self.state_history is None:
            print("Nothing to plot.")
            return


        m0, v0, h0 = self.init_cond
        ts = self.state_history[3, 0]

        match self.sim_engine:

            case 'dynamic_g':
                n = int(ts//self.dt)
                start_cond = get_start_cond(ts, self.free_fall_phase, self.dt)

                t_free = np.append(self.free_fall_phase[3, : n + 1], ts)
                m_free = np.append(self.free_fall_phase[0, : n + 1], start_cond[0])
                v_free = np.append(self.free_fall_phase[1, : n + 1], start_cond[1])
                h_free = np.append(self.free_fall_phase[2, : n + 1], start_cond[2])

                t_crash = np.append(np.array([ts]), self.free_fall_phase[3, n + 1:])
                h_crash = np.append(start_cond[2], self.free_fall_phase[2, n + 1:])
                v_crash = np.append(start_cond[1], self.free_fall_phase[1, n + 1:])

            case 'static_g':
                g = get_g()
                t_free = np.linspace(0, ts, 200)
                h_free = h0 + v0 * t_free - 0.5 * g * t_free**2
                v_free = v0 - g * t_free
                m_free = np.full_like(t_free, m0)

                t_crash = np.linspace(ts, (v0 + np.sqrt(v0**2 + 2 * g * h0)) / g, 100)
                h_crash = h0 + v0 * t_crash - 0.5 * g * t_crash**2
                v_crash = v0 - g * t_crash

        t_brake = self.state_history[3, :]
        m_brake = self.state_history[0, :]
        v_brake = self.state_history[1, :]
        h_brake = self.state_history[2, :]



        fig1, ax1 = plt.subplots(figsize=(8, 8))

        ax1.plot(
            v_crash,
            h_crash,
            color="#FF2A2A",
            linestyle="--",
            linewidth=1.5,
            label="Without braking",
        )

        ax1.plot(v_free, h_free, color="#FFB300", linewidth=2, label="Falling phase ($u=0$)")
        ax1.plot(
            v_brake, h_brake, color="#00FFAA", linewidth=2, label="Braking phase ($u=u_{max}$)"
        )

        ax1.scatter([v_free[-1]], [h_free[-1]], color="black", zorder=5)
        ax1.annotate(
            f"Activation ($t_s={ts:.1f}$ с)",
            xy=(h_free[-1], v_free[-1]),
            xytext=(15, -15),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->"),  # noqa: C408
        )

        ax1.scatter([v_brake[-1]], [h_brake[-1]], color="green", s=60, zorder=5)
        ax1.annotate(
            "Soft landing",
            xy=(h_brake[-1], v_brake[-1]),
            xytext=(15, 15),
            textcoords="offset points",
            arrowprops=dict(arrowstyle="->"),  # noqa: C408
        )

        ax1.set_ylabel("Altitude $h$, m")
        ax1.set_xlabel("Velocity $v$, m/s")
        ax1.set_title("Spacecraft phase trajectory", pad=15)

        set_plot_costomitation(ax1)
        fig1.tight_layout()
        fig1.savefig("phase_trajectory.png", dpi=300)

        fig2, (ax_m, ax_v, ax_h) = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
        plt.subplots_adjust(hspace=0.2)

        ax_m.plot(t_free, m_free, color="blue", linewidth=2)
        ax_m.plot(t_brake, m_brake, color="red", linewidth=2)
        ax_m.axvline(ts, color="gray", linestyle=":")
        ax_m.set_ylabel("Mass $m$, kg")
        ax_m.set_title("Mass flow dynamics", pad=10)
        set_plot_costomitation(ax_m)

        ax_v.plot(t_crash, v_crash, color="gray", linestyle="--")
        ax_v.plot(t_free, v_free, color="blue", linewidth=2, label="Free falling")
        ax_v.plot(t_brake, v_brake, color="red", linewidth=2, label="Active braking")
        ax_v.axvline(ts, color="gray", linestyle=":")
        ax_v.axhline(0, color="black", linewidth=0.8)
        ax_v.set_ylabel("Velocity $v$, m/s")
        ax_v.set_title("Velocity profile", pad=10)
        set_plot_costomitation(ax_v)

        ax_h.plot(t_crash, h_crash, color="gray", linestyle="--")
        ax_h.plot(t_free, h_free, color="blue", linewidth=2)
        ax_h.plot(t_brake, h_brake, color="red", linewidth=2)
        ax_h.axvline(ts, color="gray", linestyle=":")
        ax_h.axhline(0, color="black", linewidth=0.8)
        ax_h.set_ylabel("Altitude $h$, m")
        ax_h.set_xlabel("Time $t$, s")
        ax_h.set_title("Altitude profile", pad=10)

        set_plot_costomitation(ax_h)
        min_h_plot = min(np.min(h_brake), 0) - h0 * 0.05
        ax_h.set_ylim(bottom=min_h_plot)

        fig2.tight_layout()
        fig2.savefig("time_series.png", dpi=300)
        plt.show()


    def plot_residuals(self):

        alt_domain = self.final_alt[0,:]
        alt_range = self.final_alt[1,:]

        vel_domain = self.final_vel[0,:]
        vel_range = self.final_vel[1,:]

        fig, (ax_v, ax_h) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

        ax_h.plot(alt_domain, alt_range, color="blue", linewidth=2)
        ax_v.plot(vel_domain, vel_range, color="red", linewidth=2)

        ax_h.axhline(0, color="black", linewidth=0.8)
        # ax_h.axvline(ts, color="red", linestyle=":")
        # ax_h.axvline(t_min, color="green", linestyle=":",label=r"$t_{s} = t_{min}$")
        ax_h.set_ylabel("Altitude $h$, m")
        ax_h.set_xlabel("Time $t_s$, s")
        ax_h.set_title("The final altitude function plot", pad=10)
        ax_h.legend(loc="upper right")
        ax_h.grid(True)

                # ax_v.axvline(t_max, color="gray", linestyle=":")
        # ax_v.axvline(ts, color="red", linestyle=":")
        ax_v.set_ylabel("Velocity $v$, m/s")
        ax_v.set_xlabel("Time $t_s$, s")
        ax_v.set_title("The final velocity function plot", pad=10)
        ax_v.grid(True)
        ax_v.legend(loc="lower right")

        fig.tight_layout()
        fig.savefig("The final func.png", dpi=600)
        plt.show()


    # def plot_final_vel_alt_func(self):

    #     final_vel_range = self.final_vel[1,:]
    #     final_vel_domain = self.final_vel[0,:]  

    #     final_alt_range = self.final_alt[1,:]
    #     final_alt_domain = self.final_alt[0,:]

    #     ts = self.state_history[3,0]

    #     g = get_g(False)
    #     v0, h0 = self.init_cond[1], self.init_cond[2]
    #     t_min = v0 / g  if v0 > 0 else 0
    #     t_max = (v0 + np.sqrt(v0**2 + 2 * g * h0)) / g
    #     N=100
    #     left_v = np.zeros(shape=(N),dtype=np.float64)
    #     left_time_V = np.zeros_like(left_v)

    #     for i in range(N):
    #         start_cond = get_start_cond(False, self.init_cond, ts-1.2+(i)*1/N, free_fall_state= self.free_fall_phase, dt=0.1)
    #         d = shoot_kernl(False, start_cond, np.array([0,0]), ts-1.2+(i)*1/N, *self.args, mode=1)
    #         left_v[i] = d[1,-1]
    #         left_time_V[i] = ts-1.2+(i)*1/N
    #     mask = final_vel_range < ts -2
    #     vel_1 = np.append(final_vel_domain[mask],left_v)
    #     time_1 = np.append(final_vel_range[mask],left_time_V)

    #     fig, (ax_v, ax_h) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    #     ax_v.plot(time_1,vel_1, color="blue", linewidth=2)

    #     mask = (final_vel_range >=ts) & (final_vel_range<= t_max)
    #     start_cond = get_start_cond(False, self.init_cond, ts, free_fall_state= self.free_fall_phase, dt=0.1)
    #     d = shoot_kernl(False, start_cond, np.array([0,0]), ts, *self.args, mode=1)

    #     ax_v.scatter(ts,d[1,-1], color="red", s=30, zorder=5)
    #     ax_v.annotate(
    #         "Kink at the optimal switching time $t_s$",
    #         xy=(ts, d[1,-1]),
    #         xytext=(-100, 0),
    #         fontweight="bold",
    #         textcoords="offset points",
    #         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"),  # noqa: C408
    #         bbox=dict(  # noqa: C408
    #         boxstyle="round,pad=0.5", 
    #         fc="lightyellow", 
    #         ec="black",  
    #         lw=1.5,  
    #         alpha=0.9,  
    #     ),
    #     fontsize=10,
    #     )
    #     right_vel = np.append(d[1,-1], final_vel_domain[mask])
    #     rigth_time_v = np.append(ts,final_vel_range[mask])

    #     ax_v.plot(rigth_time_v,right_vel, color="blue", linewidth=2, label=r"$v(t_s, \tau) \ at \ h(t_s, \tau) = 0$")
        
    #     # ax_v.axvline(t_max, color="gray", linestyle=":")
    #     ax_v.axvline(ts, color="red", linestyle=":")
    #     ax_v.set_ylabel("Velocity $v$, m/s")
    #     ax_v.set_xlabel("Time $t_s$, s")
    #     ax_v.set_title("The final velocity function plot", pad=10)
    #     ax_v.grid(True)
    #     ax_v.legend(loc="lower right")
    #     mask = final_alt_range < t_min -0.1



    #     ax_h.plot(final_alt_range[mask], final_alt_domain[mask], color="red", linewidth=2)
    #     start_cond = get_start_cond(False, self.init_cond, t_min, free_fall_state= self.free_fall_phase, dt=1)
    #     d = shoot_kernl(False, start_cond, np.array([0,0]), t_min, *self.args, mode=0)

  
    #     mask = (t_min <= final_alt_range) & (t_max >=final_alt_range)
    #     right_alt = np.append(d[2,-1], final_alt_domain[mask])
    #     rigth_time_a = np.append(t_min, final_alt_range[mask])

    #     ax_h.scatter(t_min, d[2,-1], color="green", s=30, zorder=5)
    #     ax_h.annotate(
    #         "Kink at $h(t_{min}, \\tau)$",
    #         xy=(t_min, d[2,-1]),
    #         xytext=(0, 0),
    #         fontweight="bold",
    #         textcoords="offset points",
    #         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"),  # noqa: C408
    #         bbox=dict(  # noqa: C408
    #         boxstyle="round,pad=0.5", 
    #         fc="lightyellow", 
    #         ec="black",  
    #         lw=1.5,  
    #         alpha=0.9,  
    #     ),
    #     fontsize=10,
    #     )

    #     ax_h.plot(rigth_time_a, right_alt, color="red", linewidth=2, label=r"$h(t_s, \tau) \ at \ v(t_s, \tau)=0$")

    #     ax_h.scatter(ts, 0, color="green", s=30, zorder=5)
    #     ax_h.annotate(
    #         "Optimal time $t_s$",
    #         xy=(ts, 0),
    #         xytext=(0, 0),
    #         fontweight="bold",
    #         textcoords="offset points",
    #         arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"),  # noqa: C408
    #         bbox=dict(  # noqa: C408
    #         boxstyle="round,pad=0.5", 
    #         fc="lightyellow", 
    #         ec="black",  
    #         lw=1.5,  
    #         alpha=0.9,  
    #     ),
    #     fontsize=10,
    #     )
    #     ax_h.axhline(0, color="black", linewidth=0.8)
    #     ax_h.axvline(ts, color="red", linestyle=":")
    #     ax_h.axvline(t_min, color="green", linestyle=":",label=r"$t_{s} = t_{min}$")
    #     ax_h.set_ylabel("Altitude $h$, m")
    #     ax_h.set_xlabel("Time $t_s$, s")
    #     ax_h.set_title("The final altitude function plot", pad=10)
    #     ax_h.legend(loc="upper right")
    #     ax_h.grid(True)

    #     fig.tight_layout()
    #     fig.savefig("The final func.png", dpi=600)
    #     plt.show()
