from typing import Optional
from serial import Serial # type: ignore
from asyncio import Queue, sleep
from time import time

import numpy as np
from serial.serialutil import SerialException

from .data_model import xyzd
from .sensor import Sensor
from .constants import TLV_type, BYTE_MULT, ASYNC_SLEEP, MAGIC_NUMBER
from .utils import frame, processDetectedPoints

class IWR6843AOP(Sensor):
    """Specific sensor class for interfacing with the default board

    Args:
        Sensor (ABC): The sensor abstract base class
    """
    def __init__(self, name: str, verbose: bool=False):
        """Initialize the sensor

        Args:
            verbose (bool, optional): Print out extra initialization information, can be useful. Defaults to False.
        """
        self._is_alive: bool = False
        self._ser_config: Optional[Serial]  = None
        self._ser_data: Optional[Serial] = None
        self._verbose = verbose
        self._doppler_filtering = 0
        self._config_sent = False
        self.name = name

        # Why a queue? This is forward looking. asyncio defaults to single threaded behavior and therefore this should
        #   be thread safe by default. The upside of a queue is if this changes to a multi-process system on some executor,
        #   this code remains valid as this is a safe shared option.
        self._active_data: Queue[xyzd] = Queue(1)
        self._freq: float = 10.0
        self._last_t: float = 0.0

    def connect_config(self, com_port: str, baud_rate: int) -> bool:
        """Connect the config port. Must be done before sending config.

        Args:
            com_port (str): Port name to use
            baud_rate (int): Baud rate

        Returns:
            bool: True if successful
        """
        self._ser_config = Serial(com_port, baud_rate, timeout=1)
        self._update_alive()
        # print(self._ser_config.isOpen())
        return True

    def connect_data(self, com_port: str, baud_rate: int) -> bool:
        """Connect the data serial port. Must be done before sending config.

        Args:
            com_port (str): Port name to use
            baud_rate (int): Baud rate

        Returns:
            bool: True if successful
        """

        self._ser_data = Serial(com_port, baud_rate, timeout=1)
        self._update_alive()
        return self.is_alive()

    def _update_alive(self):
        """Internal func to verify the sensor is still connected
        """
        if self._ser_config is not None and self._ser_data is not None:  # type: ignore
            self._is_alive = self._ser_config.is_open and self._ser_data.is_open  # type: ignore

        if not self._is_alive:
            self._config_sent = False

    def is_alive(self) -> bool:
        """Getter which verifies connection

        Returns:
            bool: State of sensor connection
        """

        self._update_alive()
        return self._is_alive

    def type(self) -> Sensor.SensorType:
        """Returns sensor type

        Returns:
            Sensor.SensorType.POINT_CLOUD3D
        """
        return Sensor.SensorType.POINT_CLOUD3D

    def model(self) -> str:
        """Returns sensor type

        Returns:
            str: "IWR6843AOP"
        """
        return "IWR6843AOP"

    def send_config(self, config: list[str], max_retries: int=1) -> bool:
        """Sends config with a retry mechanism

        Args:
            config (list[str]): List of strings making up the config
            max_retries (int, optional): Number of times to retry on failure. Defaults to 1.

        Returns:
            bool: If sending was successful
        """
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
                    # print(ln)
                    # time.sleep(.2)
                    ret = self._ser_config.readline()  # type: ignore
                    if self._verbose: print(ret)  # type: ignore
                    ret = self._ser_config.readline().decode('utf-8')[:-1]  # type: ignore
                    if (ret != "Done") and (ret != "Ignored: Sensor is already stopped"):
                        failed = True
                    if self._verbose: print(ret)  # type: ignore

            if not failed:
                self._config_sent = True
                return True
        
        return False

    async def start_sensor(self) -> None:
        """Starts the sensor and will read data to a queue

        Raises:
            Exception: If sensor has some failure, will throw an exception
        """
        self._last_t = time()

        if not self._is_alive:
            raise Exception("Disconnected sensor")
        
        if not self._config_sent:
            raise Exception("Config never sent to device")

        while True:
            # Allows for context switching
            await sleep(ASYNC_SLEEP)
            try:
                chunks: list[bytes] = []
                a: Optional[bytes] = self._ser_data.read_all()  # type: ignore
                if a is None:
                    raise SerialException()
                b = MAGIC_NUMBER
                index = [x for x in range(len(a)) if a[x:x+len(b)] == b]
                # print(a)
                if len(index) > 0:
                    dt: frame = frame()

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
                            detObjRes = processDetectedPoints(bv, dt.detectedPoints_byteVecIdx, dt, raw_bv)

                            if detObjRes is not None:
                                valid_doppler = np.greater(np.abs(detObjRes.doppler), self._doppler_filtering)

                                obj_np = np.array([                                 # type: ignore
                                        detObjRes.x_coord[valid_doppler],
                                        detObjRes.y_coord[valid_doppler],
                                        detObjRes.z_coord[valid_doppler],
                                        detObjRes.doppler[valid_doppler]]).T 
                                obj: xyzd = xyzd(obj_np)

                                if self._active_data.full():
                                    self._active_data.get_nowait()
                                # print(self.name, obj.get())
                                self._active_data.put_nowait(obj)
                            
            except (IndexError, ValueError) as _:
                pass
        return None
        
    async def get_data(self) -> xyzd:
        """Returns data if it is ready

        Returns:
            data light_xyzd or none
        """
        data = await self._active_data.get()
        tt = time()
        self._freq = (1/(tt-self._last_t))*.5 + self._freq*.5
        self._last_t = tt
        return data
        

    def get_data_nowait(self) -> Optional[xyzd]:
        """Returns data if it is ready

        Returns:
            data light_xyzd or none
        """
        if(self._active_data.full()):
            tt = time()
            self._freq = (1/(tt-self._last_t))*.5 + self._freq*.5
            self._last_t = tt
            return self._active_data.get_nowait()
        
        return None


    def stop_sensor(self):
        """Close serial ports and update booleans
        """
        self._ser_config.close()  # type: ignore
        self._ser_data.close()  # type: ignore

        self._update_alive()

    def configure_filtering(self, doppler_filtering: float=0) -> bool:
        """Sets basic doppler filtering to allow static noise removal

        Args:
            doppler_filtering (float, optional): Doppler removal level, recommended to be fairly low. Defaults to 0.

        Returns:
            bool: success
        """
        self._doppler_filtering =  doppler_filtering

        return True

    def get_update_freq(self) -> float:
        """Returns the frequency that the sensor is returning data at

        Returns:
            float: Hz
        """
        return self._freq

    def __eq__(self, o: object) -> bool:
        return False

    def __repr__(self) -> str:
        return f"{self.model()} is alive: {self._is_alive} at {self._freq}Hz."