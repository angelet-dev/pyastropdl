from collections.abc import Callable

from numpy import nan

__all__ = ["halley_method"]


def halley_method(
    func: Callable[..., float],
    func_args: tuple,
    t_bounds: tuple,
    eps: float = 1e-5,
    max_iter: int = 100,
) -> float:

    t_min, t_max = t_bounds
    ti = t_max

    for _ in range(max_iter):
        
        f_val = func(ti, func_args)

        if abs(f_val) <= eps:
            return ti

        f_left = func(ti - eps, func_args)
        f_right = func(ti + eps, func_args)

        f_dx = (f_right - f_left) / (2.0 * eps)
        f_ddx = (f_right - 2.0 * f_val + f_left) / (eps**2)

        denominator = 2.0 * (f_dx**2) - f_val * f_ddx

        
        if abs(denominator) < 1e-12:
            return nan

        ti += -(2.0 * f_val * f_dx) / denominator

        if ti >= t_max:
            ti = t_max
            t_max -= 0.1
        elif ti <= t_min:
            ti = t_min
            t_min += 0.1

    return nan
