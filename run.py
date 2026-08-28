import time

from core import LunarSystemSolver
from visualization import Plotter

# === Condition of BVP ===
h_0 = 15000        
v_0 = -100        
m_0 = 15096       
init_cond = [m_0, v_0, h_0]  

h_tau = 0         
v_tau = 0        
end_cond = [v_tau, h_tau]

# === System Parameters (DPS Engine) ===
u_max = 45040      
isp = 311        
g_earth = 9.80665  

k = 3.2787 * 10 ** (-4)  
    
m_fuel = 8200     


args = (u_max, k, m_fuel)

a = time.time()
solver = LunarSystemSolver(init_cond, end_cond, args)

b = time.time()


state_history = solver.solve(is_dynamic_g=False)
# solver.find_residuals_func(is_dynamic_g=False, dt=10)
print(time.time() - b, b - a)

solver.print_results()

visialization = Plotter(solver)

# visialization.plot_final_vel_alt_func()
visialization.plot_trajectories()
