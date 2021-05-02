from abc import ABC, abstractmethod
from typing import Any, Optional
import numpy as np
from .data_model import DopplerPointCloud, ImuVelocityData, Pose
from time import time as t
from collections import deque
from scipy.spatial.transform.rotation import Rotation
from math import atan, cos, sin
from .logging import Logger, StdOutLogger
# from operator import itemgetter

# Abstract class file to contain an abstract class for all algorithms, and to contain some set of useful algos.

class Algorithm(ABC):
    """Base abstract class for all algorithms.
    """
    def __init__(self) -> None:
        super().__init__()
        self._last_called: float = t()
        self._log: Logger = StdOutLogger()

    @abstractmethod
    def reset(self) -> None:
        """Reset the state of an algorithm.
        """
        pass

    def _get_time_delta(self) -> float:
        """Get delta between two of these function calls

        Returns:
            float: Time in seconds representing the time between calls
        """
        t_called = t()
        t_delta: float = t_called - self._last_called # units are seconds
        self._last_called = t_called

        return t_delta

    def set_logger(self, new_logger: Logger):
        """Replace the default stdout logger with another.

        Args:
            new_logger (Logger): The logger to use. Must implement Logger base class.
        """
        self._logger = new_logger

    def log(self, *args: Any, **kwargs: Any) -> None:
        """Log something to the logger.
        """
        self._log.log(*args, **kwargs)

    def error(self, *args: Any, **kwargs: Any) -> None:
        """Report an error to the logger.
        """
        self._log.log(*args, **kwargs)


class SimpleMeanDistance(Algorithm):
    """An implementation of a simple point cloud algorithm. Computes the average L2 norm of the input data.
    """
    def __init__(self) -> None:
        super().__init__()

    def run(self, input: DopplerPointCloud) -> float:
        """Takes in a point cloud and returns the mean. Stateless.

        Args:
            input (DopplerPointCloud): Input point cloud, ignores doppler data.

        Returns:
            MeanFloatValue: A float representing the mean from this algorithm.
        """
        inp = input.get()
        mean_val: float = 0.0
        if inp.shape[0] > 0:
            mean_val = np.mean(np.sqrt(np.square(inp[:,:-1]).sum(axis=1))) #type: ignore

        return mean_val

    def reset(self) -> None:
        """Reset the state of an algorithm.
        """
        pass



class IMUAdjustedPersistedData(Algorithm):
    """The goal of this class is to adjust data points based on some IMU input, and persist data points through time to retain more data.
    This class will keep track of when data is fed into the algorithm, and will attempt to persist state even when some data is unavailable or poor.
    0 in construction will not allow any persistence
    """

    def __init__(self, steps_to_persist: int) -> None:
        super().__init__()
        assert steps_to_persist >= 0, "Cannot persist less than 0 states."
        self._steps: int = steps_to_persist

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

    def run(self, input_cloud: DopplerPointCloud, imu_in: ImuVelocityData) -> DopplerPointCloud:
        """Given the current Doppler point cloud with IMU data, this function will return a time adjusted point cloud.
        This point cloud will include previously entered point_clouds, which will only be as accurate as the data provided.
        Accuracy can be improved by modifying the allowable persistable steps.  

        Args:
            input_cloud (DopplerPointCloud): [description]
            imu_in (ImuData): [description]

        Returns:
            DopplerPointCloud: [description]
        """
        t_delta: float = self._get_time_delta()
        mv = imu_in.get_dxdydz()

        # Simple state estimation based on imu
        meters: tuple[float, float, float] = (mv[0]*t_delta, mv[1]*t_delta, mv[2]*t_delta)
        rot: Rotation = Rotation.from_euler('zyx', [x*t_delta for x in imu_in.get_dyawdpitchdroll()]) # type: ignore
        ret = DopplerPointCloud(input_cloud.get().copy())
        for i in self._pts:
            i.translate_rotate(meters, rot)
            ret.append(i)
        
        if len(self._pts) > self._steps:
            self._pts.popleft()

        self._pts.append(input_cloud)

        return ret

class CloudEstimatedIMU(Algorithm):
    """The goal of this class is to provide an averaged IMU output from an input point cloud data.
    It is highly reccomended to set the minium number of required points to be relatively high.
    It is wholly reasonable to state that if there are less datapoints, then it is likely that the device is not moving.
    This estimates IMU state based on an average of the input points, if there is enough data.
    """
    def __init__(self) -> None:
        super().__init__()

        self._minimum_pts = 5

    def modify_minimum_datapoints(self, val: int) -> None:
        """Modifies the number of required datapoints to generate data.

        Args:
            val (int): Any integer, negative indicates all values should be accepted. 
        """
        self._minimum_pts = val


    def run(self, data: DopplerPointCloud) -> Optional[ImuVelocityData]:
        """Accepts a doppler point cloud, and generates estimated linear and angular velocity. 

        Args:
            data (DopplerPointCloud): Cloud of data, must be of size more than the minimum to be used.
        Returns:
            Optional[ImuVelocityData]: If there are not enough data points, None. Otherwise returns an estimate of the IMU.
        """
        if data.get().shape[0] < self._minimum_pts:
            # self._logger.log(self.__class__.__name__, "WARNING: Not enough data.")
            return None
        xm: list[tuple[float, float]] = []
        ym: list[tuple[float, float]] = []
        zm: list[tuple[float, float]] = []

        raw: np.ndarray = data.get()
        for each in raw:
            doppler = each[3]
            if each[2] != 0:
                z_angle_flat_plane = atan(each[1]/each[2])
            else:
                z_angle_flat_plane = 0
            if each[0] != 0:
                x_angle_flat_plane = atan(each[1]/each[0])
            else:
                x_angle_flat_plane = 0
            xm.append((doppler * cos(x_angle_flat_plane), each[0])) # get components of velocity
            ym.append((doppler * sin(x_angle_flat_plane), each[1]))
            zm.append((doppler * cos(z_angle_flat_plane), each[2]))
            
        # xm = sorted(xm, key=itemgetter(0))
        # ym = sorted(ym, key=itemgetter(0))
        # zm = sorted(zm, key=itemgetter(0))
        if len(xm) > 0 and len(ym) > 0 and len(zm) > 0:
            xv = [x[0] for x in xm]
            yv = [x[0] for x in ym]
            zv = [x[0] for x in zm]
            xrad = [x[0]/x[1] for x in xm if x[1] != 0]
            yrad = [x[0]/x[1] for x in ym if x[1] != 0]
            zrad = [x[0]/x[1] for x in zm if x[1] != 0]


            x_mean: float = np.mean(xv) # type: ignore
            y_mean: float = np.mean(yv) # type: ignore
            z_mean: float = np.mean(zv) # type: ignore
            x_mean_rad: float = np.mean(xrad) # type: ignore
            y_mean_rad: float = np.mean(yrad) # type: ignore
            z_mean_rad: float = np.mean(zrad) # type: ignore

            # x_idx :int = np.searchsorted(xv, x_mean)
            # y_idx :int = np.searchsorted(yv, y_mean)
            # z_idx :int = np.searchsorted(zv, z_mean)

            # x_lt = 0
            # y_lt = 0
            # z_lt = 0

            # if len(xm[:x_idx]) > 0:
            #     x_lt = np.mean(xrad[:x_idx]) # average radial velocity of left side
            # if len(ym[:y_idx]) > 0:
            #     x_lt = np.mean(yrad[:y_idx])
            # if len(zm[:z_idx]) > 0:
            #     x_lt = np.mean(zrad[:z_idx])

            # x_rt = 0
            # y_rt = 0
            # z_rt = 0

            # if len(xm[x_idx:]) > 0:
            #     x_rt = np.mean(xrad[x_idx:])
            # if len(ym[y_idx:]) > 0:
            #     y_rt = np.mean(yrad[y_idx:])
            # if len(zm[z_idx:]) > 0:
            #     z_rt = np.mean(zrad[z_idx:])

            # wubble-u is = Velocity/radius. For each mean we should 

            return ImuVelocityData((x_mean, y_mean, z_mean), (x_mean_rad,y_mean_rad,z_mean_rad))
        else:
            return None

    def reset(self) -> None:
        """Reset the state of an algorithm.
        """
        pass

class EstimatedRelativePosition(Algorithm):
    """Simple computed estimate of pose with provided IMU velocity.

    Args:
        Algorithm ([type]): [description]
    """
    def __init__(self) -> None:
        super().__init__()
        self._current_pose: Pose = Pose()

    def run(self, imu_vel: ImuVelocityData, t_factor: float=1, is_moving: bool=True) -> Pose:
        """Given IMU velocity and an arbitrary optional factor, estimate current pose. This also accepts more user metadata, specifically if the sensor is actually moving.
        This may not be known, but if it is, then should be set correctly. Due to the uncertainty of the RADAR sensor, this additional data will help ensure that
        in complex scenes the algorithm does not misunderstand its movement.
        It remains important to call this function even if is_moving is false, to update the frequency of the function call.
        Args:
            imu_vel (ImuVelocityData): IMU Velocity object
            t_factor (float, optional): Optional factor to hand-tune this estimate. Simply a multiplier of time. Defaults to 1.
            is_moving (bool, optional): A boolean which can be set to false if the user knows that the sensor is not moving. Defaults to True.

        Returns:
            Pose: An estimate of the current pose
        """

        t_delta: float = self._get_time_delta()

        if is_moving:
            self._current_pose.move(imu_vel, t_delta*t_factor)

        return self._current_pose

    def reset(self) -> None:
        """Reset the state of an algorithm.
        """
        pass
