from typing import Final, Literal

from numpy import array_api, int_ as long, uint as ulong

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from typing_extensions import Never

    # `StringDType` did not exist before numpy 2.0, and we use `Never` to indicate that
    # it is not available in earlier versions, so that when used in type hints it won't
    # cause issues with type checkers, rejecting all assignments (except for `Any`).
    StringDType: TypeAlias = Never

__all__ = (
    "NUMPY_GE_1_22",
    "NUMPY_GE_1_23",
    "NUMPY_GE_1_25",
    "NUMPY_GE_2_0",
    "NUMPY_GE_2_1",
    "NUMPY_GE_2_2",
    "NUMPY_GE_2_3",
    "array_api",
    "long",
    "ulong",
)


def __dir__() -> tuple[str, ...]:
    return __all__


NUMPY_GE_1_22: Final[Literal[True]] = True  # numpy >= 1.22
NUMPY_GE_1_23: Final[Literal[True]] = True  # numpy >= 1.23
NUMPY_GE_1_25: Final[Literal[True]] = True  # numpy >= 1.25
NUMPY_GE_2_0: Final[Literal[False]] = False  # numpy >= 2.0
NUMPY_GE_2_1: Final[Literal[False]] = False  # numpy >= 2.1
NUMPY_GE_2_2: Final[Literal[False]] = False  # numpy >= 2.2
NUMPY_GE_2_3: Final[Literal[False]] = False  # numpy >= 2.3
