import numpy as np

from dataclasses import dataclass
from typing import Any, Optional
from struct import unpack

@dataclass
class light_xyzd:
    x_coord: np.ndarray
    y_coord: np.ndarray
    z_coord: np.ndarray
    doppler: np.ndarray


@dataclass(init=False)
class frame:
    """Frame class for the sensor. Only holds data attributes, similar to a struct
    """
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
    numDetectedObj: int = -1
    detectedPoints_byteVecIdx: int = -1


def getXYZ_type2(vec: list[int], vecIdx: int, Params: frame, num_detected_obj: int, sizeObj: int, raw_bv: Any):
    num_detected_obj = int(num_detected_obj)
    data = light_xyzd(np.zeros(num_detected_obj), np.zeros(num_detected_obj), np.zeros(num_detected_obj), np.zeros(num_detected_obj))  #type: ignore
    i: int
    start_idx: int

    for i in range(num_detected_obj):  
        # /*start index in bytevec for this detected obj*/
        start_idx = vecIdx + i * sizeObj
        try:
            data.x_coord[i] = unpack('f',bytes(vec[start_idx+0:start_idx+4]))[0]
            data.y_coord[i] = unpack('f',bytes(vec[start_idx+4:start_idx+8]))[0]
            data.z_coord[i] = unpack('f',bytes(vec[start_idx+8:start_idx+12]))[0]
            data.doppler[i] = unpack('f',bytes(vec[start_idx+12:start_idx+16]))[0]
        except:
            pass

    return data


def processDetectedPoints(bv: list[int], idx: int, dt: frame, raw_bv: Any) -> Optional[light_xyzd]:
    """Processes detected points from a byte vector, unpacks floats as well.
    This is some preset structure that we are breaking down
    """
    if (dt.numDetectedObj > 0):
        sizeofObj: int = 16
                
        return getXYZ_type2(bv, idx, dt, dt.numDetectedObj, sizeofObj, raw_bv)

    return None


def load_cfg_file(filepath: str) -> list[str]:
    """Load a config file to a list of strings

    Args:
        filepath (str): Filepath, relative should be ok

    Returns:
        list[str]: List of lines as str
    """
    
    assert len(filepath) > 4
    assert filepath[-4:] == ".cfg"

    data: list[str]
    with open(filepath, 'r') as f:
        data = f.readlines()
    
    return data
