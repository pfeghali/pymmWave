from abc import ABC, abstractmethod
import numpy as np
from .data_model import DopplerPointCloud, ImuData, MeanFloatValue
from time import time as t
from collections import deque


# Abstract class file to contain an abstract class for all algorithms, and to contain some set of useful algos.

class Algorithm(ABC):
    """Base abstract class for all algorithms.
    """

    @abstractmethod
    def reset(self) -> None:
        """Reset the state of an algorithm.
        """
        pass


class SimpleMeanDistance(Algorithm):
    def __init__(self) -> None:
        super().__init__()

    def run(self, input: DopplerPointCloud) -> MeanFloatValue:
        inp = input.get()
        mean_val: float = 0.0
        if inp.shape[0] > 0:
            mean_val = np.mean(np.sqrt(np.square(inp[:,:-1]).sum(axis=1))) #type: ignore

        return MeanFloatValue(mean_val)



class IMUAdjustedPersistedData(Algorithm):
    """The goal of this class is to adjust data points based on some IMU input, and persist data points through time to retain more data.
    This class will keep track of when data is fed into the algorithm, and will attempt to persist state even when some data is unavailable or poor.
    0 in construction will not allow any persistence
    """

    def __init__(self, steps_to_persist: int) -> None:
        super().__init__()
        assert steps_to_persist >= 0, "Cannot persist less than 0 states."
        self._steps: int = steps_to_persist
        self._last_called: float = t()
        self._pts: deque[DopplerPointCloud] = deque()

    def reset(self) -> None:
        """Reset the state of this algorithm, reset the state of memory, and reset the time it was last called.
        """
        self._pts = deque()
        self._last_called = t()

    def change_persisted_steps(self, new_steps: int) -> bool:
        """Will attempt to change the number of steps to persist. Will return True if successful.

        Args:
            new_steps (int): Should be greater than 0.

        Returns:
            bool: Boolean representing success
        """
        if new_steps < 0: return False
        while len(self._pts) > new_steps:
            self._pts.popleft()

        return True

    def run(self, input_cloud: DopplerPointCloud, imu_in: ImuData) -> DopplerPointCloud:
        """Given the current Doppler point cloud with IMU data, this function will return a time adjusted point cloud.
        This point cloud will include previously entered point_clouds, which will only be as accurate as the data provided.
        Accuracy can be improved by modifying the allowable persistable steps.  

        Args:
            input_cloud (DopplerPointCloud): [description]
            imu_in (ImuData): [description]

        Returns:
            DopplerPointCloud: [description]
        """
        t_called = t()
        t_delta: float = t_called-self._last_called # units are seconds
        self._last_called = t_called
        mv = imu_in.get_dxdydz()

        # Simple state estimation based on imu
        mtrs: tuple[float, float, float] = (mv[0]*t_delta, mv[1]*t_delta, mv[2]*t_delta)
        rot = imu_in.get()

        ret = DopplerPointCloud(input_cloud.get().copy())
        for i in self._pts:
            i.translate_rotate(mtrs, rot)
            ret.append(i)
        
        if len(self._pts) > self._steps:
            self._pts.popleft()

        self._pts.append(input_cloud)

        return ret