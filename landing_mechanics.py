import numpy as np


def lunar_system(Y, args):

    m, v, _ = Y
    u, g, k, min_m = args

    dh_dt = v

    if m >= min_m:
        dv_dt = (u / m) - g
        dm_dt = -u * k
    else:
        dv_dt = -g
        dm_dt = 0

    return np.array([dm_dt, dv_dt, dh_dt])


def num_sol_diff_system(F, Y0, dt, args):

    k_1 = F(Y0, args)
    k_2 = F(Y0 + (dt / 2) * k_1, args)
    k_3 = F(Y0 + (dt / 2) * k_2, args)
    k_4 = F(Y0 + dt * k_3, args)
    Y_next = Y0 + dt * (k_1 + 2 * k_2 + 2 * k_3 + k_4) / 6

    return Y_next


def free_lunar_system(t, L0, g):

    m0, v0, h0 = L0
    h = -(g * t**2) / 2 + v0 * t + h0
    v = -g * t + v0
    return np.array([m0, v, h])


def shoot(L0, t0, vtau, args, dt=0.01):

    start_cond = free_lunar_system(t0, L0, args[1])
    L = [start_cond]
    T = [t0]

    while True:
        m_prev, v_prev, h_prev = L[-1]
        t_prev = T[-1]

        m_curr, v_curr, h_curr = num_sol_diff_system(
            lunar_system, [m_prev, v_prev, h_prev], dt, args
        )

        if v_curr * v_prev <= 0:
            dv = v_curr - v_prev
            if abs(dv) > 1e-9:
                theta = (vtau - v_prev) / dv
            else:
                theta = 0

            t_final = t_prev + theta * dt

            h_final = h_prev + theta * (h_curr - h_prev)
            v_final = vtau
            m_final = m_prev + theta * (m_curr - m_prev)

            L.append([m_final, v_final, h_final])
            T.append(t_final)
            return np.array(L), T

        elif h_curr <= -L0[2]:
            return None, None

        L.append([m_curr, v_curr, h_curr])
        T.append(T[-1] + dt)


def strike_methods(L0, Ltau, args, dt=10, eps=0.00001):

    _, g, _, _ = args
    t0 = L0[1] / g

    t1, t2 = t0, t0 + dt

    L, T = shoot(L0, t1, Ltau[0], args, dt)
    F1 = L[-1, 2]

    L, T = shoot(L0, t2, Ltau[0], args, dt)
    F2 = L[-1, 2]
    i = 1
    while abs(F2) >= Ltau[1] + eps:
        i += 1
        if F1 * F2 < 0:
            dt *= 0.5
            t2 = t1 + dt
        else:
            t1 = t2
            F1 = F2
            t2 = t1 + dt

        L, T = shoot(L0, t2, Ltau[0] + eps, args)
        F2 = L[-1, 2]

    return L, T
