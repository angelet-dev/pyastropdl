from numba import njit

from pyastropdl.core.utils.types import StateVector, f64_1d, i64, void


@njit(void(f64_1d, f64_1d, f64_1d, i64), cache=True, fastmath=True)
def lerp_inplace(
    curr_state: StateVector,
    prev_state: StateVector,
    end_state: StateVector,
    mode: int
) -> None:

    # mode: 0 - velocity, 1 - altitude
    theta = 0.0

    match mode:
        case 0:
            dv = curr_state[1] - prev_state[1]
            theta = (end_state[0] - prev_state[1]) / dv if abs(dv) > 1e-9 else 0.0
        case 1:
            dh = curr_state[2] - prev_state[2]
            theta = (end_state[1] - prev_state[2]) / dh if abs(dh) > 1e-9 else 0.0

    for i in range(4):
        curr_state[i] = prev_state[i] + theta * (curr_state[i] - prev_state[i])
