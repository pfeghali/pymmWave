from abc import ABC, abstractmethod
from typing import Optional
from .data_model import DataModel
from scipy.spatial.transform.rotation import Rotation
from enum import Enum


class Sensor(ABC):
    """
    Base sensor class. The goal of this class implementation is such that users can implement classes which can then be used with our library of algorithms easily.
    """

    class SensorType(Enum):
        """Enum class for sensor types
        """
        IMU = 1
        POINT_CLOUD3D = 2
        POINT_CLOUD2D = 3

    @abstractmethod
    def type(self) -> 'Sensor.SensorType':
        """Return the type of a sensor

        Returns:
            str: Type of sensor
        """
        pass

    @abstractmethod
    def model(self) -> str:
        """Return the model of a sensor

        Returns:
            str: Name of sensor
        """
        pass
    
    @abstractmethod
    def is_alive(self) -> bool:
        """Check if sensor is still alive

        Returns:
            bool: True if alive
        """
        pass

    @abstractmethod
    async def start_sensor(self) -> None:
        """Asynchronous loop that can be run as a corouting with asyncio, or other asynchronous libraries.

        Returns:
            Nothing, will be run as a coroutine!
        """
        pass

    @abstractmethod
    def stop_sensor(self):
        """Stop sensor

        Returns:
            Nothing, kills everything
        """
        pass

    @abstractmethod
    async def get_data(self) -> DataModel:
        """Return data from sensor.
        """
        pass

    @abstractmethod
    def get_data_nowait(self) -> Optional[DataModel]:
        """Return data from sensor if available, otherwise None.

        Returns:
            Optional[DopplerPointCloud]: Data if there is data available, otherwise returns None.
        """
        pass

    @abstractmethod
    def get_update_freq(self) -> float:
        """Returns the sensor update freq. This is reccommended to be the actual rate of data access.
        """
        pass

class SpatialSensor(object):
    """Wrapper to provide the notion of a sensor in space
    """
    def __init__(self, sens: Sensor, location: tuple[float, float, float], pitch_rads: tuple[float, float, float]):
        self.sensor = sens
        self.location = location
        
        # This speeds up code later
        self.pitch_rads: Rotation = Rotation.from_rotvec(pitch_rads) #type: ignore


class InvalidSensorException(Exception):
    def __init__(self, message: str, errors: str):
        super().__init__(message)


if __name__ == "__main__":
    x = Sensor.SensorType.POINT_CLOUD3D
    print(type(x))