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

EXAMPLE_CONFIG: list[str] = ["""% ***************************************************************\n""",
"""% Created for SDK ver:03.04""",
"""% Created using Visualizer ver:3.5.0.0""",
"""% Frequency:60""",
"""% Platform:xWR68xx_AOP""",
"""% Scene Classifier:best_range_res""",
"""% Azimuth Resolution(deg):60 + 60""",
"""% Range Resolution(m):0.044""",
"""% Maximum unambiguous Range(m):9.02""",
"""% Maximum Radial Velocity(m/s):1.21""",
"""% Radial velocity resolution(m/s):0.16""",
"""% Frame Duration(msec):50""",
"""% ***************************************************************""",
"""sensorStop""",
"""flushCfg""",
"""dfeDataOutputMode 1""",
"""channelCfg 15 7 0""",
"""adcCfg 2 1""",
"""adcbufCfg -1 0 1 1 1""",
"""profileCfg 0 60 975 7 57.14 0 0 70 1 256 5209 0 0 158""",
"""chirpCfg 0 0 0 0 0 0 0 1""",
"""frameCfg 0 0 16 0 40 1 0""",
"""lowPower 0 0""",
"""guiMonitor -1 1 1 0 0 0 1""",
"""cfarCfg -1 0 2 8 4 3 0 15 0""",
"""cfarCfg -1 1 0 4 2 3 1 15 1""",
"""multiObjBeamForming -1 1 0.5""",
"""clutterRemoval -1 0""",
"""calibDcRangeSig -1 0 -5 8 256""",
"""extendedMaxVelocity -1 0""",
"""lvdsStreamCfg -1 0 0 0""",
"""compRangeBiasAndRxChanPhase 0.0 1 0 -1 0 1 0 -1 0 1 0 -1 0 1 0 -1 0 1 0 -1 0 1 0 -1 0""",
"""measureRangeBiasAndRxChanPhase 0 1.5 0.2""",
"""CQRxSatMonitor 0 3 5 121 0""",
"""CQSigImgMonitor 0 127 4""",
"""analogMonitor 0 0""",
"""aoaFovCfg -1 -90 90 -90 90""",
"""cfarFovCfg -1 0 0 8.92""",
"""cfarFovCfg -1 1 -1.21 1.21""",
"""sensorStart"""]