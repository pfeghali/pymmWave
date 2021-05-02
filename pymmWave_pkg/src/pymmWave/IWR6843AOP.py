from dataclasses import dataclass
from typing import Any, Optional
from struct import unpack

from serial import Serial # type: ignore
from asyncio import Queue, sleep
from time import time

import numpy as np
from serial.serialutil import SerialException

from .data_model import DopplerPointCloud
from .sensor import Sensor
from .constants import TLV_type, BYTE_MULT, ASYNC_SLEEP, MAGIC_NUMBER

class IWR6843AOP(Sensor):
    """Abstract :obj:`Sensor<mmWave.sensor.Sensor>` class implementation for interfacing with the COTS TI IWR6843AOP evaluation board.
    Can be initialized with a public 'name', which can be used for sensor reference. This class supports point-cloud retrieval with doppler information on a per-point basis.
    The class can also be designed to automatically filter by doppler data to limit noisy data points.
    """
    def __init__(self, name: str, verbose: bool=False):
        """Initialize the sensor

        Args:
            verbose (bool, optional): Print out extra initialization information, can be useful. Defaults to False.
        """
        super().__init__()
        self._is_alive: bool = False
        self._ser_config: Optional[Serial]  = None
        self._ser_data: Optional[Serial] = None
        self._verbose = verbose
        self._doppler_filtering = 0
        self._config_sent = False
        self.name = name
        self._config_port_name: Optional[str] = None
        self._data_port_name: Optional[str] = None
        self._config_baud: Optional[int] = None
        self._data_baud: Optional[int] = None

        # Why a queue? This is forward looking. asyncio defaults to single threaded behavior and therefore this should
        #   be thread safe by default. The upside of a queue is if this changes to a multi-process system on some executor,
        #   this code remains valid as this is a safe shared option.
        self._active_data: Queue[DopplerPointCloud] = Queue(1)
        self._freq: float = 10.0
        self._last_t: float = 0.0

    @dataclass
    class _light_doppler_cloud:
        x_coord: np.ndarray
        y_coord: np.ndarray
        z_coord: np.ndarray
        doppler: np.ndarray



    @dataclass(init=False)
    class _frame:
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


    def _getXYZ_type2(self, vec: list[int], vecIdx: int, Params: _frame, num_detected_obj: int, sizeObj: int, raw_bv: Any):
        num_detected_obj = int(num_detected_obj)
        data = self._light_doppler_cloud(np.zeros(num_detected_obj), np.zeros(num_detected_obj), np.zeros(num_detected_obj), np.zeros(num_detected_obj))  #type: ignore
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


    def _processDetectedPoints(self, bv: list[int], idx: int, dt: _frame, raw_bv: Any) -> Optional[_light_doppler_cloud]:
        """Processes detected points from a byte vector, unpacks floats as well.
        This is some preset structure that we are breaking down
        """
        if (dt.numDetectedObj > 0):
            sizeofObj: int = 16
                    
            return self._getXYZ_type2(bv, idx, dt, dt.numDetectedObj, sizeofObj, raw_bv)

        return None



    def connect_config(self, com_port: str, baud_rate: int, timeout: int=1) -> bool:
        """Connect to the config port. Must be done before sending config.
        This function will timeout after a second by default. This timeout period is low since programmatically connecting to serial ports might be difficult with long timeout periods, as it is difficult to know apriori if you are connecting to config or data.

        Args:
            com_port (str): Port name to use
            baud_rate (int): Baud rate
            timeout (int, optional): Timeout. Defaults to 1.

        Returns:
            bool: True if successful

        Example:
            On MacOS, for example:

            >>> my_sensor.connect_config('/dev/tty.SLAB_USBtoUART4', 115200)
            True

        """
        try:
            self._ser_config = Serial(com_port, baud_rate, timeout=timeout)
        except SerialException as e:
            print(e)
            return False
        except FileNotFoundError:
            print(f"{com_port} is an invalid serial port.")
            return False
        except ValueError:
            print("Baud rate is invalid.")
            return False

        self._update_alive()
        self._config_port_name = com_port
        self._config_baud = baud_rate

        return True

    def connect_data(self, com_port: str, baud_rate: int, timeout: int=1) -> bool:
        """Connect the data serial port. Must be done before sending config.

        Args:
            com_port (str): Port name to use
            baud_rate (int): Baud rate
            timeout (int, optional): Timeout. Defaults to 1.

        Returns:
            bool: True if successful

        Example:
            On MacOS, for example:

            >>> my_sensor.connect_data('/dev/tty.SLAB_USBtoUART', 921600)
            True
        """

        try:
            self._ser_data = Serial(com_port, baud_rate, timeout=timeout)
        except SerialException as e:
            print(e)
            return False
        except FileNotFoundError:
            print(f"{com_port} is an invalid serial port.")
            return False
        except ValueError:
            print("Baud rate is invalid.")
            return False

        self._update_alive()
        self._data_port_name = com_port
        self._data_baud = baud_rate

        return True



    def _update_alive(self):
        """Internal func to verify the sensor is still connected
        """
        if self._ser_config is not None and self._ser_data is not None:  # type: ignore
            self._is_alive = self._ser_config.is_open and self._ser_data.is_open  # type: ignore

        if not self._is_alive:
            self._config_sent = False

    def is_alive(self) -> bool:
        """Getter which verifies connection to this particular sensor.

        Returns:
            bool: True if the sensor is still connected.
        """

        self._update_alive()
        return self._is_alive

    def type(self) -> Sensor.SensorType:
        """Returns enum :obj:`Sensor.SensorType<mmWave.Sensor.SensorType>`

        Returns:
            Sensor.SensorType.POINT_CLOUD3D
        """
        return Sensor.SensorType.POINT_CLOUD3D

    def model(self) -> str:
        """Returns the particular model number supported with this class.

        Returns:
            str: "IWR6843AOP"
        """
        return "IWR6843AOP"

    def send_config(self, config: list[str], max_retries: int=1, autoretry_cfg_data: bool=True) -> bool:
        """Tried to send a TI config, with a simple retry mechanism.
        Configuration files can be created here: `https://dev.ti.com/gallery/view/mmwave/mmWave_Demo_Visualizer/ver/3.5.0/`. Future support may be built for creating configuration files.

        Args:
            config (list[str]): List of strings making up the config
            max_retries (int, optional): Number of times to retry on failure. Defaults to 1.

        Returns:
            bool: If sending was successful

        Raises:
            SerialException: If device is disconnected before completion, SerialExceptions may be raised.
        """
        valid_replies = set(["Done", "Ignored: Sensor is already stopped"])
        if not self._is_alive:
            self._config_sent = False
            return False

        attempts = 0
        failed = False
        while attempts < max_retries:
            attempts += 1
            failed = False
            for line in config:
                if line[0] == '%' or line[0] == '\n':
                    pass
                else:
                    ln = line.replace('\r','')
                    self._ser_config.write(ln.encode())  # type: ignore

                    try:
                        ret1 = self._ser_config.readline()  # type: ignore
                        ret1 = ret1.decode('utf-8')[:-1].strip()   # type: ignore
                    except UnicodeDecodeError:
                        ret1 = "error"

                    try:
                        ret = self._ser_config.readline()   # type: ignore
                        ret = ret.decode('utf-8')[:-1].strip()  # type: ignore
                    except UnicodeDecodeError:
                        ret = "error"

                    # We look at both replies just in case of an error in ordering of results. Rare, but can happen.
                    if not ((ret1 in valid_replies) or (ret in valid_replies)):
                        failed = True
                        self.log("invalid replies:", ret1, ret)
                        self.error("Sending configuration failed!")
                        break
                    # if self._verbose: self.log(ret_str)  # type: ignore

            if not failed:
                self._config_sent = True
                return True
        
        # There are various reasons for failure. One of the more common is due to swapping of cfg/data.
        if not autoretry_cfg_data:
            return False

        # we need to close config/data connections, and attempt to reconnect.
        # Swaps ports and their baud rates. Trying to reopen connections just does not work.
        self.log("Attempting to auto-resolve configuration error.")
        self._ser_config.reset_output_buffer()   # type: ignore
        self._ser_data.reset_output_buffer()   # type: ignore
        self._ser_config.reset_input_buffer()   # type: ignore
        self._ser_data.reset_input_buffer()   # type: ignore
        self._ser_config.baudrate = self._data_baud   # type: ignore
        self._ser_data.baudrate = self._config_baud  # type: ignore
        tmp = self._ser_data   # type: ignore
        self._ser_data = self._ser_config   # type: ignore
        self._ser_config = tmp


        self.log(f"Swapped opened config ({self._config_port_name}) and data ports ({self._data_port_name}).")
        self.log("Retrying configuration.")
        return self.send_config(config, max_retries, autoretry_cfg_data=False)

    async def start_sensor(self) -> None:
        """Starts the sensor and will place data into a queue.
        The goal of this function is to manage the state of the entire application. Nothing will happen if this function is not run with asyncio.
        This function attempts to read data from the sensor as quickly as it can, then extract positional+doppler data, and place data into an asyncio.Queue.
        Since this relies on the asyncio Queue, limitations may stem from asyncio. These issues, mainly revolving around thread safety, can be dealt with at the application layer.

        This function also actively attempts to context switch between intervals to minimize overhead.

        Raises:
            Exception: If sensor has some failure, will throw a SerialException.
        """
        self._last_t = time()

        if not self._is_alive:
            raise Exception("Disconnected sensor")
        
        if not self._config_sent:
            raise Exception("Config never sent to device")
        a: Optional[bytes] = b''
        while True:
            # Allows for context switching
            await sleep(ASYNC_SLEEP)
            try:
                chunks: list[bytes] = []
                a += self._ser_data.read_all()  # type: ignore
                if a is None:
                    raise SerialException()
                b = MAGIC_NUMBER
                index = [x for x in range(len(a)) if a[x:x+len(b)] == b]
                # print(len(a))
                if len(index) > 0:

                    dt = self._frame()
                    # Header
                    byteVecIdx = index[0]+8 # magic word (4 unit16)
                    #numDetectedObj = 0
                    # Version, uint32: MajorNum * 2^24 + MinorNum * 2^16 + BugfixNum * 2^8 + BuildNum
                    dt.tlv_version = a[byteVecIdx:byteVecIdx + 4]
                    dt.tlv_version_uint16 = dt.tlv_version[2] + (dt.tlv_version[3] << 8)
                    byteVecIdx += 4

                    bf = np.array([x for x in a[byteVecIdx:byteVecIdx + 4]])  # type: ignore
                    b_m = np.array(BYTE_MULT)  # type: ignore
                    # Total packet length including header in Bytes, uint32
                    totalPacketLen = int(np.sum(np.dot(bf, b_m)))  # type: ignore
                    byteVecIdx += 4
                    chunks.append(a)
                    chunks.append(self._ser_data.read(totalPacketLen-8))  # type: ignore
                    bv = [x for x in b''.join(chunks)]
                    raw_bv = b''.join(chunks)
                    
                    if (len(bv) >= totalPacketLen):
                        # print("VALID", totalPacketLen, len(bv))

                        #platform type, uint32: 0xA1643 or 0xA1443 
                        dt.tlv_platform = np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT))  # type: ignore
                        byteVecIdx += 4

                        # Frame number, uint32
                        dt.frameNumber = np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT))  # type: ignore
                        byteVecIdx += 4

                        # Time in CPU cycles when the message was created. For AR16xx: DSP CPU cycles
                        # timeCpuCycles = np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT))  # type: ignore
                        byteVecIdx += 4

                        # Number of detected objects, uint32
                        dt.numDetectedObj = np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT))  # type: ignore
                        byteVecIdx += 4

                        # Number of TLVs, uint32
                        numTLVs = int(np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT)))  # type: ignore
                        byteVecIdx += 4

                        # print("Objs:", dt.numDetectedObj, numTLVs)

                        byteVecIdx += 4

                        #  start_tlv_ticks: int
                        for _ in range(numTLVs):
                            if(byteVecIdx>len(bv)):
                                break
                            tlv_type = np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT))  # type: ignore
                            byteVecIdx += 4
                            tlv_length = int(np.sum(np.dot(bv[byteVecIdx:byteVecIdx + 4], BYTE_MULT)))  # type: ignore
                            byteVecIdx += 4
                            # print(numTLVs, tlv_type, tlv_
                            # length)

                            # tlv payload
                            if (TLV_type(tlv_type) == TLV_type.MMWDEMO_OUTPUT_MSG_DETECTED_POINTS):
                                # will not get this type if numDetectedObj == 0 even though gui monitor selects this type
                                dt.detectedPoints_byteVecIdx = byteVecIdx
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_RANGE_PROFILE):
                            #     #Params.rangeProfile_byteVecIdx = byteVecIdx
                            #     pass
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_NOISE_PROFILE):
                            #     # processRangeNoiseProfile(bytevec, byteVecIdx, Params, false)
                            #     # gatherParamStats(Params.plot.noiseStats, getTimeDiff(start_tlv_ticks))
                            #     pass
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_AZIMUT_STATIC_HEAT_MAP):
                            #     pass
                            #     # processAzimuthHeatMap(bytevec, byteVecIdx, Params)
                            #     # gatherParamStats(Params.plot.azimuthStats, getTimeDiff(start_tlv_ticks))
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_RANGE_DOPPLER_HEAT_MAP):
                            #     pass
                            #     # processRangeDopplerHeatMap(bytevec, byteVecIdx, Params)
                            #     # gatherParamStats(Params.plot.dopplerStats, getTimeDiff(start_tlv_ticks))
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_STATS):
                            #     pass
                            #     # processStatistics(bytevec, byteVecIdx, Params)
                            #     # gatherParamStats(Params.plot.cpuloadStats, getTimeDiff(start_tlv_ticks))
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_DETECTED_POINTS_SIDE_INFO):
                            #     pass
                            #     # Params.sideInfo_byteVecIdx = byteVecIdx
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_AZIMUT_ELEVATION_STATIC_HEAT_MAP):
                            #     pass
                            #     # processAzimuthElevHeatMap(bytevec, byteVecIdx, Params)
                            #     # gatherParamStats(Params.plot.azimuthElevStats, getTimeDiff(start_tlv_ticks))
                            # elif (tlv_type == TLV_type.MMWDEMO_OUTPUT_MSG_TEMPERATURE_STATS):
                            #     pass
                            #     # processTemperatureStatistics(bytevec, byteVecIdx, Params)
                            #     # gatherParamStats(Params.plot.temperatureStats, getTimeDiff(start_tlv_ticks))
                            

                            byteVecIdx += tlv_length
                        
                        # print("TLV loop took {} seconds".format(time.time()-st_tlv))
                        if(dt.detectedPoints_byteVecIdx > -1):
                            detObjRes = self._processDetectedPoints(bv, dt.detectedPoints_byteVecIdx, dt, raw_bv)

                            if detObjRes is not None:
                                valid_doppler = np.greater(np.abs(detObjRes.doppler), self._doppler_filtering)

                                obj_np = np.array([                                 # type: ignore
                                        detObjRes.x_coord[valid_doppler],
                                        detObjRes.y_coord[valid_doppler],
                                        detObjRes.z_coord[valid_doppler],
                                        detObjRes.doppler[valid_doppler]]).T 
                                obj: DopplerPointCloud = DopplerPointCloud(obj_np)

                                if self._active_data.full():
                                    self._active_data.get_nowait()
                                # print(self.name, obj.get())
                                self._active_data.put_nowait(obj)
                    a = b''
                else:
                    pass
                    # print("No data.")
            except (IndexError, ValueError) as _:
                pass
        return None
        
    async def get_data(self) -> DopplerPointCloud:
        """Returns data when it is ready. This function also updates the frequency measurement of the sensor.
        This function is blocking.

        Returns:
            DopplerPointCloud: [description]
        """
        data = await self._active_data.get()
        tt = time()
        self._freq = (1/(tt-self._last_t))*.5 + self._freq*.5
        self._last_t = tt
        return data
        

    def get_data_nowait(self) -> Optional[DopplerPointCloud]:
        """Returns data if it is ready, otherwise none. This function also updates the frequency measurement of the sensor if data is available.

        Returns:
            Optional[DopplerPointCloud]: Data if there is data available, otherwise returns None.
        """
        if(self._active_data.full()):
            tt = time()
            self._freq = (1/(tt-self._last_t))*.5 + self._freq*.5
            self._last_t = tt
            return self._active_data.get_nowait()
        
        return None

    def stop_sensor(self):
        """This function attempts to close all serial ports and update internal state booleans.
        """
        try:
            self._ser_config.close()  # type: ignore
            self._ser_data.close()  # type: ignore
        except SerialException:
            pass
        self._update_alive()

    def configure_filtering(self, doppler_filtering: float=0) -> bool:
        """Sets basic doppler filtering to allow for static noise removal.
        Doppler filtering sets a floor for doppler results, to remove points less than the input.

        Args:
            doppler_filtering (float, optional): Doppler removal level, recommended to be fairly low. Defaults to 0.

        Returns:
            bool: success
        """
        self._doppler_filtering =  doppler_filtering

        return True

    def get_update_freq(self) -> float:
        """Returns the frequency that the sensor is returning data at. This is not equivalent to the true capacity of the sensor, but rather the rate which the application is successfully getting data.

        Returns:
            float: Hz
        """
        return self._freq

    def __eq__(self, o: object) -> bool:
        return False

    def __repr__(self) -> str:
        return f"{self.model()} is alive: {self._is_alive} at {self._freq}Hz."