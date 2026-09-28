from typing import Annotated, Any, TypeAlias

import matplotlib.animation as manim
import matplotlib.axes as maxes
import matplotlib.figure as mfig
import matplotlib.lines as mlines
import matplotlib.offsetbox as mbox
import numba as nb
import numpy as np
from numpy.typing import NDArray

from pyastropdl.core.utils.paths import Path

f64 = nb.float64
i64 = nb.int64
nb_str = nb.types.unicode_type
nb_bool = nb.boolean
void = nb.void

f64_1d = nb.float64[:]
f64_2d = nb.float64[:, :]
                    
f64_tuple3 = nb.types.UniTuple(nb.float64, 3) 
f64_tuple2 = nb.types.UniTuple(nb.float64, 2) 
f64_tuple4 = nb.types.UniTuple(nb.float64, 4) 

f64_1d_bool = nb.types.Tuple((f64_1d, nb_bool))
f64_2d_bool = nb.types.Tuple((f64_2d, nb_bool))

FloatArray = NDArray[np.float64]
Vector = NDArray[np.float64]
StateVector: TypeAlias = Annotated[NDArray[np.float64], "Shape: (2,) | (3,) | (4,)"]

PathType: TypeAlias = Path
AnyType: TypeAlias = Any
MplAxes: TypeAlias = maxes.Axes
MplFigure: TypeAlias = mfig.Figure
MplLine: TypeAlias = mlines.Line2D
MplAnim: TypeAlias = manim.FuncAnimation
MplAnchoredBox: TypeAlias = mbox.AnchoredOffsetbox
MplTextArea: TypeAlias = mbox.TextArea
