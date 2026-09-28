import numpy as np

from .types import FloatArray, Vector


def get_data_bounds(arrays: tuple[FloatArray, ...] | FloatArray) -> Vector | None:
    if arrays is None:
        return None

    if isinstance(arrays, np.ndarray):
        items = (arrays,)
    elif isinstance(arrays, tuple) and len(arrays) > 0:
        items = arrays
    else:
        return None

    first_shape = items[0].shape

    if len(first_shape) == 1:
        g_min = min(np.min(a) for a in items)
        g_max = max(np.max(a) for a in items)
        return np.array([g_min, g_max], dtype=np.float64)

    rows = first_shape[0]
    data_limits = np.empty(rows * 2, dtype=np.float64)

    for i in range(rows):
        data_limits[2 * i] = min(np.min(a[i, :]) for a in items)
        data_limits[2 * i + 1] = max(np.max(a[i, :]) for a in items)

    return data_limits