import numpy as np
from typing import Any, Optional

class light_xyzd:
    x_coord: np.ndarray
    y_coord: np.ndarray
    z_coord: np.ndarray
    doppler: np.ndarray
    def __init__(self, x_coord: Any, y_coord: Any, z_coord: Any, doppler: Any) -> None: ...

class frame:
    packet: float
    idxPacket: float
    header: float
    detObj: float
    rp: float
    np: float
    tlv_version: bytes
    tlv_version_uint16: int
    tlv_platform: int
    frameNumber: int
    numDetectedObj: int = ...
    detectedPoints_byteVecIdx: int = ...

def getXYZ_type2(vec: list[int], vecIdx: int, Params: frame, numDetecObj: int, sizeObj: int, raw_bv: Any) -> Any: ...
def processDetectedPoints(bv: list[int], idx: int, dt: frame, raw_bv: Any) -> Optional[light_xyzd]: ...
def load_cfg_file(filepath: str) -> list[str]: ...
