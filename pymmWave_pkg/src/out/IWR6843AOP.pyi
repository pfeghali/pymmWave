from .data_model import xyzd as xyzd
from .sensor import Sensor as Sensor
from typing import Any, Optional

class IWR6843AOP(Sensor):
    name: Any = ...
    def __init__(self, name: Any, verbose: bool=...) -> None: ...
    def connect_config(self, com_port: str, baud_rate: int) -> bool: ...
    def connect_data(self, com_port: str, baud_rate: int) -> bool: ...
    def is_alive(self) -> bool: ...
    def type(self) -> Sensor.SensorType: ...
    def model(self) -> str: ...
    def send_config(self, config: list[str], max_retries: int=...) -> bool: ...
    async def start_sensor(self) -> None: ...
    async def get_data(self) -> xyzd: ...
    def get_data_nowait(self) -> Optional[xyzd]: ...
    def stop_sensor(self) -> None: ...
    def configure_filtering(self, doppler_filtering: float=...) -> bool: ...
    def get_update_freq(self) -> float: ...
    def __eq__(self, o: object) -> bool: ...