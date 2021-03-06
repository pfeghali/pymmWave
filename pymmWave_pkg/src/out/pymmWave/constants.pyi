from enum import Enum
from typing import Any

BYTE_MULT: Any

class TLV_type(Enum):
    MMWDEMO_OUTPUT_MSG_DETECTED_POINTS: int = ...
    MMWDEMO_OUTPUT_MSG_RANGE_PROFILE: int = ...
    MMWDEMO_OUTPUT_MSG_NOISE_PROFILE: int = ...
    MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP: int = ...
    MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP: int = ...
    MMWDEMO_OUTPUT_MSG_STATS: int = ...
    MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO: int = ...
    MMWDEMO_OUTPUT_MSG_AZIMUT_ELEVATION_STATIC_HEAT_MAP: int = ...
    MMWDEMO_OUTPUT_MSG_TEMPERATURE_STATS: int = ...
    MMWDEMO_OUTPUT_MSG_MAX: int = ...

ASYNC_SLEEP: float
MAGIC_NUMBER: bytes
EXAMPLE_CONFIG: list[str]
