from abc import ABC, abstractmethod
from typing import Any
import numpy as np
from scipy.spatial.transform.rotation import Rotation

class DataModel(ABC):
    """
    Base Data Class
    """

    @abstractmethod
    def get(self) -> Any:
        """Get the underlying value
        """
        pass

class DopplerPointCloud(DataModel):
    """Fairly lightweight class for X, Y, Z, and doppler data.
    """
    def __init__(self, data: np.ndarray): 
        """Initialize a DopplerPointCloud object and verify the input shape is valid.

        Args:
            data (np.ndarray): Nx4 size numpy.ndarray.
        """
        assert len(data.shape) == 2
        assert data.shape[1] == 4

        self._data: np.ndarray = data

    def get(self) -> np.ndarray:
        """Gets the underlying data container.

        Returns:
            np.ndarray: The underlying data matrix.
        """
        return self._data

    def translate_rotate(self, location: tuple[float, float, float], pitch_rads: Rotation):
        """Translates and rotates the underlying object. This is done in-place, no further verification is done.

        Args:
            location (Tuple[float, float, float]): Tuple of float values to shift the underlying data with: (x meters, y meters, z meters)
            pitch_rads (Rotation): Rotation matrix object from scipy.spatial.transform.rotation.Rotation
        """
        if self._data.shape[0]:
            self._data[:,0] += location[0]
            self._data[:,1] += location[1]
            self._data[:,2] += location[2]
            self._data[:,:3] = pitch_rads.apply(self._data[:,:3])  #type: ignore

    def append(self, other: 'DopplerPointCloud') -> bool:
        """Append another DopplerPointCloud object to this one in-place

        Args:
            other (DopplerPointCloud): Another object of the same type

        Returns:
            bool: If success, true.
        """
        self._data = np.concatenate(self._data, other._data)

        return True

    def __eq__(self, o: object) -> bool:
        return False

    def __repr__(self) -> str:
        return self._data.__repr__()

class ImuVelocityData(DataModel):
    """Class to represent a velocity data point from the IMU.

    Args:
        DataModel ([type]): [description]
    """
    def __init__(self, dxdydz: tuple[float, float, float], drolldpitchdyaw: tuple[float, float, float]) -> None:
        self._dxdydz: tuple[float, float, float] = dxdydz
        self._drolldpitchdyaw: tuple[float, float, float] = drolldpitchdyaw
        self._rot: Rotation = Rotation.from_euler('zyx', [self._drolldpitchdyaw]) #type: ignore

    def get(self) -> Rotation:
        """This is a get representing the change in roll/pitch/yaw. This will need to be time adjusted to be useful.

        Returns:
            Rotation: [description]
        """
        return self._rot

    def get_dxdydz(self) -> tuple[float, float, float]:
        return self._dxdydz

    def get_drolldpitchdyaw(self) -> tuple[float, float, float]:
        return self._drolldpitchdyaw

class ImuData(DataModel):
    def __init__(self, altitude: float, dxdydz: tuple[float, float, float], drolldpitchdyaw: tuple[float, float, float], heading: float) -> None:
        self._altitude: float = altitude
        self._dxdydz: tuple[float, float, float] = dxdydz
        self._drolldpitchdyaw: tuple[float, float, float] = drolldpitchdyaw
        self._heading: float = heading
        self._rot: Rotation = Rotation.from_euler('zyx', [self._drolldpitchdyaw])  #type: ignore

    def get(self) -> Rotation:
        """This is a get representing the change in roll/pitch/yaw. This will need to be time adjusted to be useful.

        Returns:
            Rotation: [description]
        """
        return self._rot

    def get_altitude(self) -> float:
        return self._altitude

    def get_heading(self) -> float:
        return self._heading

    def get_dxdydz(self) -> tuple[float, float, float]:
        return self._dxdydz

    def get_drolldpitchdyaw(self) -> tuple[float, float, float]:
        return self._drolldpitchdyaw



class _speed_constraints(DataModel):
    def __init__(self, max_x: tuple[float, float], max_y: tuple[float, float], max_z: tuple[float, float]) -> None:
        self._max_x = max_x
        self._max_y = max_y
        self._max_z = max_z

    def get_max_x(self) -> tuple[float, float]:
        return self._max_x

    def get_max_y(self) -> tuple[float, float]:
        return self._max_y

    def get_max_z(self) -> tuple[float, float]:
        return self._max_z

class Pose(DataModel):
    """A generic representation of pose. The goal is to support basic operations on representations of current physical state.
    """
    def __init__(self) -> None:
        super().__init__()
        self._x = 0
        self._y = 0
        self._z = 0
        self._yaw = 0
        self._pitch = 0
        self._roll = 0

    def move(self, imu_vel: ImuVelocityData, time_passed: float):
        """Based on some IMU velocity information and the amount of time which has passed, modify the current pose.

        Args:
            imu_vel (ImuVelocityData): Input IMU data.
            time_passed (float): Time in seconds.
        """
        rot_vec: np.ndarray = (Rotation.from_euler('zyx', [self._roll, self._pitch, self._yaw]) ).apply(imu_vel.get_dxdydz()) * time_passed

        self._x += rot_vec[0]
        self._y += rot_vec[1]
        self._z += rot_vec[2]
        self._yaw += imu_vel.get_drolldpitchdyaw()[0] * time_passed
        self._pitch += imu_vel.get_drolldpitchdyaw()[1] * time_passed
        self._roll += imu_vel.get_drolldpitchdyaw()[2] * time_passed

    def get(self) -> tuple[float, float, float, float, float, float]:
        """Returns a tuple representing x, y, z position, and roll, pitch, yaw.

        Returns:
            tuple[float, float, float, float, float, float]: (x, y, z, roll, pitch, yaw)
        """
        return (self._x, self._y, self._z, self._roll, self._pitch, self._yaw)