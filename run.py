import time

from core import LunarSystemSolver
from visualization import Plotter

# === Condition of BVP ===
h_0 = 50000        
v_0 = 250        
m_0 = 450       
init_cond = [m_0, v_0, h_0]  

h_tau = 0         
v_tau = 0        
end_cond = [v_tau, h_tau]

# === System Parameters (DPS Engine) ===
u_max = 600      
isp = 311        
g_earth = 9.80665  

k = 2.883 * 10 ** (-4)  
    
m_fuel = 300     


args = (u_max, k, m_fuel)
solver = LunarSystemSolver(init_cond, end_cond, args)

a = time.time()
state_history = solver.solve('dynamic_g')
b = time.time()



# solver.find_residuals(is_dynamic_g=False, dt=1)
print(b - a)

solver.print_results()



visialization = Plotter(solver)

# visialization.plot_residuals()
visialization.plot_trajectories()






# import matplotlib.pyplot as plt
# import numpy as np

# from visualization import set_dark_theme, set_plot_costomitation

# set_dark_theme()

# arr_1 = np.array([5000,4500,3400, 3000])
# arr_2 = np.array([-30, -50, -70, -71])
# arr_3 = np.linspace(0, 70, 8)

# arr_5 = np.array([3000, 2400, 1300, 400, 0])
# arr_6 = np.array([-71, -60, -40, -30, -20])

# fig1, ax1 = plt.subplots(figsize=(8, 8))

# # ax1.plot(
# #             v_crash,
# #             h_crash,
# #             color="#FF2A2A",
# #             linestyle="--",
# #             linewidth=1.5,
# #             label="Without braking",
# #         )

# ax1.plot(arr_2, arr_1, color="#e8a403", linewidth=2, label="Falling phase ($u=0$)")
# ax1.plot(arr_6, arr_5, color="#04dd95", linewidth=2, label="Braking phase ($u=u_{max}$)")

# ax1.plot([arr_2[-1]], [arr_1[-1]], color="#04dd95", marker='o', markersize=8 ,linewidth=2)


# ax1.set_ylabel("Altitude $h$, m")
# ax1.set_xlabel("Velocity $v$, m/s")
# ax1.set_title("Spacecraft phase trajectory", pad=15)

# set_plot_costomitation(ax1)


# fig1.tight_layout()

# plt.show()