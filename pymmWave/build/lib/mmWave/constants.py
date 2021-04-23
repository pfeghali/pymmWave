from math import pow
from enum import Enum

# Constant from TI - lets not touch this
BYTE_MULT = [1, 256, pow(2, 16), pow(2, 24)]

# Constant from TI - used for basic recognition.
class TLV_type(Enum):
    MMWDEMO_OUTPUT_MSG_DETECTED_POINTS= 1
    MMWDEMO_OUTPUT_MSG_RANGE_PROFILE= 2
    MMWDEMO_OUTPUT_MSG_NOISE_PROFILE= 3
    MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP= 4
    MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP= 5
    MMWDEMO_OUTPUT_MSG_STATS= 6
    MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO= 7
    MMWDEMO_OUTPUT_MSG_AZIMUT_ELEVATION_STATIC_HEAT_MAP= 8
    MMWDEMO_OUTPUT_MSG_TEMPERATURE_STATS= 9
    MMWDEMO_OUTPUT_MSG_MAX= 10


# Sleep value to allow for thread context switching.
# Can reduce or increase, but frankly, I wouldn't unless you have a good reason.
ASYNC_SLEEP: float = .000001

# Straight up magic number from TI...
MAGIC_NUMBER: bytes = b'\x02\x01\x04\x03\x06\x05\x08\x07'