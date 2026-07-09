from landing_mechanics import strike_methods
from utils import plot_trajectories


# === Condition of BVP ===
v_0 = 100
h_0 = 100000
m_0 = 224
init_cond = [m_0, v_0, h_0]

v_tau = 0
h_tau = 0
end_cond = [v_tau, h_tau]

# === System Parameters ===
m_fuel = 204
min_m = m_0 - m_fuel
u = 400
k = 2.883 * 10 ** (-3)
g = 1.622
args = (u, g, k, min_m)

state_history, time_steps = strike_methods(init_cond, end_cond, args, eps=10e-8)
m_ts, v_ts, h_ts = state_history[0]
m_tau, v_tau, h_tau = state_history[-1]

results = f"""
=========================================================================
                       LUNAR SOFT LANDING RESULTS                  
=========================================================================
 Parameter          |  Engine Switching (t_s)  |  Terminal Landing (tau)
-------------------------------------------------------------------------
 Time (s)           |  {time_steps[0]:>22.2f}  |  {time_steps[-1]:>22.2f}
 Altitude (m)       |  {h_ts:>22.2f}  |  {h_tau:>22.2f}
 Velocity (m/s)     |  {v_ts:>22.2f}  |  {v_tau:>22.2f}
 Vehicle Mass (kg)  |  {m_ts:>22.2f}  |  {m_tau:>22.2f}
=========================================================================
"""
print(results)
plot_trajectories(init_cond, time_steps, state_history, g)
