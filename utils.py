import numpy as np
import matplotlib.pyplot as plt


def plot_trajectories(init_cond, time_steps, state_history, g):

    plt.rcParams.update(
        {
            "text.usetex": False,
            "axes.labelsize": 12,
            "font.size": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    m0, v0, h0 = init_cond
    ts = time_steps[0]

    t_free = np.linspace(0, ts, 200)
    h_free = h0 + v0 * t_free - 0.5 * g * t_free**2
    v_free = v0 - g * t_free
    m_free = np.full_like(t_free, m0)

    t_brake = np.array(time_steps)
    m_brake = state_history[:, 0]
    v_brake = state_history[:, 1]
    h_brake = state_history[:, 2]

    t_crash = np.linspace(ts, (v0 + np.sqrt(v0**2 + 2 * g * h0)) / g, 100)
    h_crash = h0 + v0 * t_crash - 0.5 * g * t_crash**2
    v_crash = v0 - g * t_crash

    fig1, ax1 = plt.subplots(figsize=(8, 8))

    ax1.plot(
        v_crash,
        h_crash,
        color="gray",
        linestyle="--",
        linewidth=1.5,
        label="Without braking",
    )

    ax1.plot(v_free, h_free, color="blue", linewidth=2, label="Falling phase ($u=0$)")
    ax1.plot(
        v_brake, h_brake, color="red", linewidth=2, label="Braking phase ($u=u_{max}$)"
    )

    ax1.scatter([v_free[-1]], [h_free[-1]], color="black", zorder=5)
    ax1.annotate(
        f"Activation ($t_s={ts:.1f}$ с)",
        xy=(h_free[-1], v_free[-1]),
        xytext=(15, -15),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->"),
    )

    ax1.scatter([v_brake[-1]], [h_brake[-1]], color="green", s=60, zorder=5)
    ax1.annotate(
        "Soft landing",
        xy=(h_brake[-1], v_brake[-1]),
        xytext=(15, 15),
        textcoords="offset points",
        arrowprops=dict(arrowstyle="->"),
    )

    ax1.set_ylabel("Height $h$, m")
    ax1.set_xlabel("Velocity $v$, m/s")
    ax1.set_title("Spacecraft phase trajectory", pad=15)
    ax1.grid(True)
    # ax1.invert_yaxis()
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig("phase_trajectory.png", dpi=300)

    fig2, (ax_m, ax_v, ax_h) = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    plt.subplots_adjust(hspace=0.2)

    ax_m.plot(t_free, m_free, color="blue", linewidth=2)
    ax_m.plot(t_brake, m_brake, color="red", linewidth=2)
    ax_m.axvline(ts, color="gray", linestyle=":")
    ax_m.set_ylabel("Mass $m$, kg")
    ax_m.set_title("Mass flow dynamics", pad=10)
    ax_m.grid(True)

    ax_v.plot(t_crash, v_crash, color="gray", linestyle="--")
    ax_v.plot(t_free, v_free, color="blue", linewidth=2, label="Free falling")
    ax_v.plot(t_brake, v_brake, color="red", linewidth=2, label="Active braking")
    ax_v.axvline(ts, color="gray", linestyle=":")
    ax_v.axhline(0, color="black", linewidth=0.8)
    ax_v.set_ylabel("Velocity $v$, m/s")
    ax_v.set_title("Velocity profile", pad=10)
    ax_v.grid(True)
    ax_v.legend(loc="lower left")

    ax_h.plot(t_crash, h_crash, color="gray", linestyle="--")
    ax_h.plot(t_free, h_free, color="blue", linewidth=2)
    ax_h.plot(t_brake, h_brake, color="red", linewidth=2)
    ax_h.axvline(ts, color="gray", linestyle=":")
    ax_h.axhline(0, color="black", linewidth=0.8)
    ax_h.set_ylabel("Height $h$, m")
    ax_h.set_xlabel("Time $t$, s")
    ax_h.set_title("Height profile", pad=10)
    ax_h.grid(True)

    min_h_plot = min(np.min(h_brake), 0) - h0 * 0.05
    ax_h.set_ylim(bottom=min_h_plot)

    fig2.tight_layout()
    fig2.savefig("time_series.png", dpi=300)
    plt.show()
