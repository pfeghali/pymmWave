"""
This type stub file was generated by pyright.
"""

from typing import Optional
from .data_model import xyzd
from .sensor import Sensor

class IWR6843AOP(Sensor):
    """Specific sensor class for interfacing with the default board

    Args:
        Sensor (ABC): The sensor abstract base class
    """
    def __init__(self, name, verbose=...) -> None:
        """Initialize the sensor

        Args:
            verbose (bool, optional): Print out extra initialization information, can be useful. Defaults to False.
        """
        ...
    
    def connect_config(self, com_port: str, baud_rate: int) -> bool:
        """Connect the config port. Must be done before sending config.

        Args:
            com_port (str): Port name to use
            baud_rate (int): Baud rate

        Returns:
            bool: True if successful
        """
        ...
    
    def connect_data(self, com_port: str, baud_rate: int) -> bool:
        """Connect the data serial port. Must be done before sending config.

        Args:
            com_port (str): Port name to use
            baud_rate (int): Baud rate

        Returns:
            bool: True if successful
        """
        ...
    
    def is_alive(self) -> bool:
        """Getter which verifies connection

        Returns:
            bool: State of sensor connection
        """
        ...
    
    def type(self) -> Sensor.SensorType:
        """Returns sensor type

        Returns:
            Sensor.SensorType.POINT_CLOUD3D
        """
        ...
    
    def model(self) -> str:
        """Returns sensor type

        Returns:
            str: "IWR6843AOP"
        """
        ...
    
    def send_config(self, config: list[str], max_retries: int = ...) -> bool:
        """Sends config with a retry mechanism

        Args:
            config (list[str]): List of strings making up the config
            max_retries (int, optional): Number of times to retry on failure. Defaults to 1.

        Returns:
            bool: If sending was successful
        """
        ...
    
    async def start_sensor(self):
        """Starts the sensor and will read data to a queue

        Raises:
            Exception: If sensor has some failure, will throw an exception
        """
        ...
    
    async def get_data(self) -> xyzd:
        """Returns data if it is ready

        Returns:
            data light_xyzd or none
        """
        ...
    
    def get_data_nowait(self) -> Optional[xyzd]:
        """Returns data if it is ready

        Returns:
            data light_xyzd or none
        """
        ...
    
    def stop_sensor(self):
        """Close serial ports and set bools
        """
        ...
    
    def configure_filtering(self, doppler_filtering: float = ...) -> bool:
        """Sets basic doppler filtering to allow static noise removal

        Args:
            doppler_filtering (float, optional): Doppler removal level, recommended to be fairly low. Defaults to 0.

        Returns:
            bool: success
        """
        ...
    
    def get_update_freq(self) -> float:
        """Returns the frequency that the sensor is returning data at

        Returns:
            float: Hz
        """
        ...
    
    def __eq__(self, o: object) -> bool:
        ...
    
    def __repr__(self) -> str:
        ...
    


