from abc import ABC, abstractmethod
from typing import Optional
from .data_model import DataModel, xyzd
from scipy.spatial.transform.rotation import Rotation
from enum import Enum

class Sensor(ABC):
    """
    Base Sensor Class
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
        """While true loop that will start the sensor

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
    async def get_data(self) -> xyzd:
        """Return data from sensor.
        """
        pass

    @abstractmethod
    def get_data_nowait(self) -> Optional[xyzd]:
        """Return data from sensor.
        """
        pass

    @abstractmethod
    def get_update_freq(self) -> float:
        """Return sensor update freq.
        """
        pass

class SpatialSensor(object):
    """Wrapper to provide the notion of a sensor in space
    TODO: It could be fun to make another class which si a similair wrapper and
        preprocesses data to be in the right orientation at point of usage
    """
    def __init__(self, sens: Sensor, location: tuple[float, float, float], pitch_rads: tuple[float, float, float]):
        self.sensor = sens
        self.location = location
        
        # This speeds up code later
        self.pitch_rads: Rotation = Rotation.from_rotvec(pitch_rads)


class InvalidSensorException(Exception):
    def __init__(self, message: str, errors):
        super().__init__(message)


if __name__ == "__main__":
    x = Sensor.SensorType.POINT_CLOUD3D
    print(type(x))