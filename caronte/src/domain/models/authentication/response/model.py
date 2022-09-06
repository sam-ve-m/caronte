# Caronte
from caronte.src.domain.enums.response import CaronteStatus

# Standards
from enum import Enum
from typing import NewType, Tuple, Union

# Third party
from aioredlock import Lock


class LockAuthenticationStatus(Enum):
    SUCCESS = 0
    INTERNAL_LOCK_ERROR = 1
    ACQUIRING_LOCK_ERROR = 2
    RUNTIME_LOCK_ERROR = 3
    INTERNAL_SERVER_ERROR = 4


class UnlockAuthenticationStatus(Enum):
    SUCCESS = 0
    INTERNAL_LOCK_ERROR = 1
    ACQUIRING_LOCK_ERROR = 2
    RUNTIME_LOCK_ERROR = 3
    INTERNAL_SERVER_ERROR = 4


CaronteStatusResponse = NewType(
    "CaronteStatusResponse", Tuple[bool, CaronteStatus, Union[dict, None]]
)
LockAuthenticationResponse = NewType(
    "LockAuthenticationResponse", Tuple[bool, LockAuthenticationStatus, Lock]
)
UnlockAuthenticationResponse = NewType(
    "UnlockAuthenticationResponse", Tuple[bool, UnlockAuthenticationStatus]
)
