from typing import Final, Literal

import numpy as array_api
from numpy import long, ulong

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from typing_extensions import Never
    from numpy import dtype

    # there were no `numpy.dtypes.StringDType` typing stubs before numpy 2.1, but
    # because it has no scalar type we use `Never` to indicate its absence.
    StringDType: TypeAlias = dtype[Never]
else:
    from numpy.dtypes import StringDType


__all__ = (
    "NUMPY_GE_1_22",
    "NUMPY_GE_1_23",
    "NUMPY_GE_1_25",
    "NUMPY_GE_2_0",
    "NUMPY_GE_2_1",
    "NUMPY_GE_2_2",
    "NUMPY_GE_2_3",
    "StringDType",
    "array_api",
    "long",
    "ulong",
)


def __dir__() -> tuple[str, ...]:
    return __all__


NUMPY_GE_1_22: Final[Literal[True]] = True  # numpy >= 1.22
NUMPY_GE_1_23: Final[Literal[True]] = True  # numpy >= 1.23
NUMPY_GE_1_25: Final[Literal[True]] = True  # numpy >= 1.25
NUMPY_GE_2_0: Final[Literal[True]] = True  # numpy >= 2.0
NUMPY_GE_2_1: Final[Literal[False]] = False  # numpy >= 2.1
NUMPY_GE_2_2: Final[Literal[False]] = False  # numpy >= 2.2
NUMPY_GE_2_3: Final[Literal[False]] = False  # numpy >= 2.3
