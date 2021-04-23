"""
This type stub file was generated by pyright.
"""

import numpy as np
from abc import ABC
from scipy.spatial.transform.rotation import Rotation

class DataModel(ABC):
    """"
    Base Data Class
    """
    ...


class xyzd(DataModel):
    """Wrapper class for X, Y, Z, and doppler data.
    """
    def __init__(self, data: np.ndarray) -> None:
        """Initialize a XYZD object and verify shape is valid.

        Args:
            data (np.ndarray): Nx4 size ndarray.
        """
        ...
    
    def get(self) -> np.ndarray:
        """Gets the underlying data

        Returns:
            np.ndarray: Data in object
        """
        ...
    
    def translate_rotate(self, location: tuple[float, float, float], pitch_rads: Rotation):
        """Translates and rotates the underlying object. This is done in-place, no further verification is done.

        Args:
            location (Tuple[float, float, float]): Tuple of float values to shift the underlying data with: (x mtrs, y mtrs, z mtrs)
            pitch_rads (Rotation): Rotation matrix object from scipy.spatial.transform.rotation.Rotation
        """
        ...
    
    def append(self, other: xyzd) -> bool:
        """Append another XYZD object to this one in-place

        Args:
            other (xyzd): Another object of the same type

        Returns:
            bool: If success, true.
        """
        ...
    
    def __eq__(self, o: object) -> bool:
        ...
    
    def __repr__(self) -> str:
        ...
    


class PotentialCollisions(DataModel):
    """Notion of a potentil collision - currently unused.
    """
    def __init__(self, front: bool, back: bool, left: bool, right: bool) -> None:
        ...
    
    def get(self) -> tuple[bool, bool, bool, bool]:
        ...
    


class imu_data(DataModel):
    def __init__(self, altitude: float, dxdydz: tuple[float, float, float], yawpitchroll: tuple[float, float, float], heading: float) -> None:
        ...
    
    def get_altitude(self) -> float:
        ...
    
    def get_heading(self) -> float:
        ...
    
    def get_dxdydz(self) -> tuple[float, float, float]:
        ...
    
    def get_yawpitchroll(self) -> tuple[float, float, float]:
        ...
    


class speed_constraints(DataModel):
    def __init__(self, max_x: tuple[float, float], max_y: tuple[float, float], max_z: tuple[float, float]) -> None:
        ...
    
    def get_max_x(self) -> tuple[float, float]:
        ...
    
    def get_max_y(self) -> tuple[float, float]:
        ...
    
    def get_max_z(self) -> tuple[float, float]:
        ...
    


