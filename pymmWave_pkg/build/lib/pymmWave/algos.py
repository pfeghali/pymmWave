from abc import ABC
import numpy as np
from .data_model import DopplerPointCloud, MeanFloatValue
# Abstract class file to contain an abstract class for all algorithms, and to contain some set of useful algos.

class Algorithm(ABC):
    """Base abstract class for all algorithms.
    """

class SimpleMeanDistance(Algorithm):
    def __init__(self) -> None:
        super().__init__()

    def run(self, input: DopplerPointCloud) -> MeanFloatValue:
        inp = input.get()
        mean_val: float = 0.0
        if inp.shape[0] > 0:
            mean_val = np.mean(np.sqrt(np.square(inp[:,:-1]).sum(axis=1)))

        return MeanFloatValue(mean_val)